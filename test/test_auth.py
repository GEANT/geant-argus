import pytest

from geant_argus.auth import get_groups_from_entitlements


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
