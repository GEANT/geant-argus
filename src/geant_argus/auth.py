import functools
import re

from argus.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group

from geant_argus.geant_argus.view_helpers import error_response

OIDC_AUTHORIZATION_RULES = getattr(settings, "OIDC_AUTHORIZATION_RULES", None)
OIDC_SUPERUSER_GROUP = getattr(settings, "ARGUS_OIDC_SUPERUSER_GROUP", None)
DJANGO_WRITE_PERMSSION_GROUP = "editors"


def update_groups(response, user: User, *args, **kwargs):
    if not OIDC_AUTHORIZATION_RULES:
        return

    assert user, "User must be set"
    new_group_names = get_groups_from_entitlements(
        response.get("entitlements", []), rules=OIDC_AUTHORIZATION_RULES
    )
    user.groups.set(g for g in Group.objects.all() if g.name in new_group_names)

    is_superuser = OIDC_SUPERUSER_GROUP in new_group_names if OIDC_SUPERUSER_GROUP else False
    user.is_superuser = user.is_staff = is_superuser

    user.save()


def get_groups_from_entitlements(entitlements, rules):
    """Read the oidc entitlements and apply them to the OIDC_AUTHORIZATION_RULES to obtain a set
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
