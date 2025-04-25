import functools
import re
from django.conf import settings
from argus.auth.models import User
from django.contrib.auth.models import Group
from django.contrib import messages

from geant_argus.geant_argus.view_helpers import error_response

OIDC_AUTHORIZATION_RULES = getattr(settings, "OIDC_AUTHORIZATION_RULES", None)
OIDC_SUPERUSER_GROUP = getattr(settings, "ARGUS_OIDC_SUPERUSER_GROUP", None)


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
    result = set()
    for candidate in entitlements:
        for rule in rules:
            match rule:
                case {"entitlement": entitlement, "group": group}:
                    if entitlement == candidate:
                        result.add(group)
                case {"entitlement_pattern": pattern, "group": group}:
                    if match := re.match(pattern, candidate):
                        result.add(group.format(**match.groupdict()))
                case _:
                    pass
    return result


def has_write_permission(user):
    return "editors" in {g.name for g in user.groups.all()}


def require_write(refresh_target="home", methods=None):
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
