import datetime
from unittest.mock import call, patch

import pytest
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory
from django.utils import timezone
from django_htmx.middleware import HtmxMiddleware
from social_core.pipeline.social_auth import associate_user
from social_django.storage import DjangoUserMixin
from social_django.utils import load_backend, load_strategy

from geant_argus import auth


@pytest.mark.parametrize(
    "entitlements, groups",
    [
        (["something", "some-entitlement", "something-else"], {"some-group"}),
        (["some-entitlement", "pattern:pattern-group:suffix"], {"pattern-group", "some-group"}),
    ],
)
def test_get_groups_from_entitlements(entitlements, groups):
    rules = [
        {"entitlement": "some-entitlement", "group": "some-group"},
        {"entitlement_pattern": "pattern:(?P<group>\\S+):suffix", "group": "{group}"},
    ]
    assert set(auth.get_groups_from_entitlements(entitlements, rules)) == groups


@pytest.fixture
def http_request(default_user):
    request = RequestFactory().get("/not-relevant")
    request.user = default_user
    SessionMiddleware(lambda x: x).process_request(request)
    MessageMiddleware(lambda x: x).process_request(request)
    HtmxMiddleware(lambda x: x)(request)
    return request


@pytest.mark.django_db
class TestRequireWrite:
    @pytest.fixture
    def protected_view(self):
        @auth.require_write()
        def _protected_view(request):
            _protected_view.called = True
            return HttpResponse(b"")

        _protected_view.called = False
        return _protected_view

    def test_protected_view(self, http_request, protected_view):
        protected_view(http_request)
        assert protected_view.called

    def test_protected_view_with_unauthorized_user(self, http_request, protected_view):
        http_request.user.groups.set([])
        http_request.user.save()
        protected_view(http_request)
        assert not protected_view.called


@pytest.fixture(autouse=True)
def use_dummy_oidc_backend(settings):
    settings.SOCIAL_AUTH_AUTHENTICATION_BACKENDS = [
        "geant_argus.testing.social_auth.FakeOpenIDConnectAuth"
    ]


@pytest.fixture
def social_auth_user(use_dummy_oidc_backend, default_user):
    strategy = load_strategy()
    backend = load_backend(strategy, "oidc", redirect_uri="")
    social: DjangoUserMixin = associate_user(backend, "1234", default_user)["social"]
    social.set_extra_data({"auth_token": "old-token", "refresh_token": "old-refresh-token"})
    return default_user


@pytest.mark.django_db
class TestSocialAuthRefreshMiddleware:

    @pytest.fixture
    def middleware(self):
        return auth.SocialAuthRefreshMiddleware(lambda x: x)

    def test_new_session_is_not_expired(self, middleware, http_request):
        assert not middleware.auth_needs_recheck(http_request)

    def test_refreshes_auth_when_expired(self, middleware, http_request, social_auth_user):
        assert social_auth_user.social_auth.first().extra_data["auth_token"] == "old-token"
        middleware.update_auth_recheck(http_request, expire_after=datetime.timedelta(seconds=-1))
        middleware(http_request)
        assert social_auth_user.social_auth.first().extra_data["auth_token"] == "auth-token"

    def test_no_longer_expired_after_refresh(self, middleware, http_request, social_auth_user):
        middleware.update_auth_recheck(http_request, expire_after=datetime.timedelta(seconds=-1))
        assert middleware.auth_needs_recheck(http_request)
        middleware(http_request)
        assert not middleware.auth_needs_recheck(http_request)

    def test_updates_groups(self, middleware, http_request, social_auth_user):
        middleware.update_auth_recheck(http_request, expire_after=datetime.timedelta(seconds=-1))
        with patch.object(auth, "update_user_from_entitlements") as obj:
            middleware(http_request)

        # see geant_argus.testing.social_auth.FakeOpenIDConnectAuth for the entitlements values
        assert obj.call_args == call(http_request.user, ["some-entitlement"])


@pytest.mark.django_db
class TestSocialAuthLimitSessionAgeMiddleware:
    social_auth_max_session_age = datetime.timedelta(hours=24)

    @pytest.fixture
    def middleware(self):
        return auth.SocialAuthLimitSessionAgeMiddleware(lambda x: x)

    def test_expires_social_auth_session_quickly(self, middleware, http_request, social_auth_user):
        middleware(http_request)
        assert (
            http_request.session.get_expiry_date()
            <= timezone.now() + self.social_auth_max_session_age
        )

    def test_normal_user_session_doesnt_expire_quickly(self, middleware, http_request):
        middleware(http_request)
        assert (
            http_request.session.get_expiry_date()
            > timezone.now() + self.social_auth_max_session_age
        )
