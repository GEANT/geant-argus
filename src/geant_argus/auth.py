import datetime
import functools
import logging
import re

import requests
from argus.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy
from django.contrib.auth import logout
from geant_argus.geant_argus.view_helpers import error_response, redirect

logger = logging.getLogger(__name__)

DJANGO_WRITE_PERMSSION_GROUP = "editors"
DJANGO_SUPERUSER_GROUP = "admin"


def update_groups(response, user: User, *args, **kwargs):
    """python_social_auth pipeline function"""
    assert user, "User must be set"
    update_user_from_entitlements(user, response.get("entitlements", []))


def update_user_from_entitlements(user: User, entitlements: list[str]):
    authorization_rules = getattr(settings, "OIDC_AUTHORIZATION_RULES", None)

    if not authorization_rules:
        return

    new_group_names = get_groups_from_entitlements(entitlements, rules=authorization_rules)
    user.groups.set(g for g in Group.objects.all() if g.name in new_group_names)

    is_superuser = DJANGO_SUPERUSER_GROUP in new_group_names if DJANGO_SUPERUSER_GROUP else False
    user.is_superuser = user.is_staff = is_superuser
    user.save()


def get_groups_from_entitlements(entitlements, rules):
    """Read the oidc entitlements and apply them to the rules to obtain a set
    of Django groups that the user should have. Currently there are two kinds of rules. The first
    is an entitlement rule to one-to-one map an entitlement to a group::

        {
            "entitlement": "some:entitlement:string",
            "group": "some-group"
        }

    The second one is an entitlement pattern to use regex to capture groups from a class of
    entitlements an construct a group name based on the result. The named regex capture groups
    can be used to create a group name using python ``format`` style string interpolation::

        {
            "entitlement_pattern": "prefix:(?P<group>\\S+)#aai.geant.org",
            "group": "{group}-members"
        }

    The above example would mean that a user with an entitlement ``prefix:swd#aai.geant.org``
    would be added to the ``swd-members`` group. Keep in mind that the regex should be constructed
    in such a way to prevent accidental matches.
    """
    groups = set()
    for candidate in entitlements:
        for rule in rules:
            match rule:
                case {"entitlement": str(entitlement), "group": str(group)}:
                    if entitlement == candidate:
                        groups.add(group)
                case {"entitlement_pattern": str(pattern), "group": str(group)}:
                    if match := re.match(pattern, candidate):
                        groups.add(group.format(**match.groupdict()))
                case _:
                    pass
    return groups


def has_write_permission(user):
    return DJANGO_WRITE_PERMSSION_GROUP in {g.name for g in user.groups.all()}


def require_write(refresh_target="home", methods=None):
    """A decorator that can be used for a django view function. It protects the view so that
    only users who have write permission can access it. Any user who does not have the correct
    permissions gets redirected to the ``refresh_target`` view and is given an error message.

    :param refresh_target: The view name to redirect the user to in case they do not have
        sufficient permissions
    :param methods: An optional iterable of HTTP methods. if given, only protect these methods,
        such as ``"POST"`` or ``"DELETE"``. If not given, protect all http methods
    """
    methods = set(m.upper() for m in methods) if methods is not None else None

    def _decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            is_guarded_method = methods is None or request.method.upper() in methods
            if is_guarded_method and (not request.user or not has_write_permission(request.user)):
                messages.error(request, "Insufficient permissions")
                return error_response(request, refresh_target)
            return view_func(request, *args, **kwargs)

        return wrapper

    return _decorator


class SocialAuthRefreshMiddleware(MiddlewareMixin):
    """After a user has succesfully logged in using social auth (ie. oidc), by default there
    are no further checks whether a user has additional authorizations granted or revoked. That is
    the responsibility of this middleware. It periodically (AUTH_RECHECK_INTERVAL_SECONDS)
    refreshes the access token and updates the user data, which contains the entitlements. It then
    updates the groups of the user according to this entitlements and the OIDC_AUTHORIZATION_RULES

    If the refresh_token has been invalidated, for example because the user has been deactivated
    by the authorization provider, the user is logged out of Argus and redirected to the login
    page.
    """

    SOCIAL_AUTH_PROVIDER = "oidc"
    AUTH_RECHECK_INTERVAL = datetime.timedelta(minutes=5)

    def process_request(self, request):
        if self.auth_needs_recheck(request):
            self.refresh_auth(request)
            self.update_auth_recheck(request)

    def auth_needs_recheck(self, request):
        try:
            auth_recheck = datetime.datetime.fromisoformat(request.session["auth_recheck"])
        except (KeyError, ValueError, TypeError):
            # When users have an invalid auth_recheck timestamp we update it to a valid one
            # and then give them the benefit of the doubt that we don't need to recheck them
            # eg. for users that have just logged in
            self.update_auth_recheck(request)
            return False
        return datetime.datetime.now() > auth_recheck

    def update_auth_recheck(self, request, expire_after: datetime.timedelta | None = None):
        expire_after = expire_after or self.AUTH_RECHECK_INTERVAL
        request.session["auth_recheck"] = (datetime.datetime.now() + expire_after).isoformat()

    def refresh_auth(self, request):
        user = request.user
        if not hasattr(user, "social_auth"):
            return

        social: UserSocialAuth = user.social_auth.get(provider=self.SOCIAL_AUTH_PROVIDER)

        if not social:
            return

        strategy = load_strategy()
        backend = social.get_backend_instance(strategy)
        assert hasattr(backend, "user_data"), "auth backend must have user_data method"

        try:
            social.refresh_token(strategy)
            access_token = social.get_access_token(strategy)
            user_data = backend.user_data(access_token)
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                messages.error(
                    "You have been logged out, "
                    "your OIDC provided account may have been deactivated"
                )
                logout(request)
                return redirect(request, "home")

            # other errors may indicate some other failure that is not due to the acount being
            # deactivated
            return
        except (requests.exceptions.RequestException, OSError):
            logger.exception("An error occured when validating the user's auth status")
            return

        if entitlements := user_data.get("entitlements"):
            update_user_from_entitlements(request.user, entitlements)


class SocialAuthLimitSessionAgeMiddleware(MiddlewareMixin):
    SOCIAL_AUTH_PROVIDER = "oidc"
    SOCIAL_AUTH_USER_MAX_SESSION_AGE = datetime.timedelta(hours=24)

    def process_response(self, request, response):
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "social_auth") or not user.social_auth.first():
            return response

        if not (session := getattr(request, "session", None)):
            return response

        max_expiry = timezone.now() + self.SOCIAL_AUTH_USER_MAX_SESSION_AGE
        expiry = session.get_expiry_date()
        session["_session_expiry"] = min(expiry, max_expiry).isoformat()
        return response
