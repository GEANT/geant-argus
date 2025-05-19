from django.http import HttpResponse
from django.test import RequestFactory
import pytest
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django_htmx.middleware import HtmxMiddleware

from geant_argus.auth import get_groups_from_entitlements, require_write


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
    assert set(get_groups_from_entitlements(entitlements, rules)) == groups


@pytest.mark.django_db
class TestRequireWrite:
    @pytest.fixture
    def http_request(self, default_user):
        request = RequestFactory().get("/not-relevant")
        request.user = default_user
        SessionMiddleware(lambda x: x).process_request(request)
        MessageMiddleware(lambda x: x).process_request(request)
        HtmxMiddleware(lambda x: x)(request)
        return request

    @pytest.fixture
    def protected_view(self):
        @require_write()
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
