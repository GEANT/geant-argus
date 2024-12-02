import re
from django.conf import settings
from argus.auth.models import User
from django.contrib.auth.models import Group

OIDC_ENTITLEMENTS_PATTERN = getattr(settings, "ARGUS_OIDC_ENTITLEMENTS_PATTERN", None)
OIDC_SUPERUSER_GROUP = getattr(settings, "ARGUS_OIDC_SUPERUSER_GROUP", None)


def update_groups(response, user: User, *args, **kwargs):
    if not OIDC_ENTITLEMENTS_PATTERN:
        return

    assert user, "User must be set"

    pattern = re.compile(OIDC_ENTITLEMENTS_PATTERN, re.IGNORECASE)
    new_group_names = set(
        match.group("group")
        for entitlement in response.get("entitlements", [])
        if (match := re.match(pattern, entitlement))
    )

    user.groups.set(g for g in Group.objects.all() if g.name in new_group_names)

    is_superuser = OIDC_SUPERUSER_GROUP in new_group_names if OIDC_SUPERUSER_GROUP else False
    user.is_superuser = user.is_staff = is_superuser

    user.save()
