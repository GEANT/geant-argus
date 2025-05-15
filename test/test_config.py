import jsonschema
import pytest

from geant_argus.settings.config import CONFIG_SCHEMA


def default_config():
    return {"SEND_EXPIRED_BLACKLISTS_EMAILS_TO": []}


def test_validate_authorization_rules():
    config = {
        **default_config(),
        "OIDC_AUTHORIZATION_RULES": [
            {"entitlement": "some-entitlement", "group": "some-group"},
            {"entitlement_pattern": "pattern:(?P<group>\\S+):suffix", "group": "{group}"},
        ],
    }
    jsonschema.validate(config, CONFIG_SCHEMA)


@pytest.mark.parametrize(
    "rule, message",
    [
        ({}, "is not valid"),
        ({"something": "else"}, "Additional properties are not allowed"),
        ({"entitlement": 123, "group": "asdf"}, "is not of type 'string'"),
        ({"entitlement": "asdf", "group": 123}, "is not of type 'string'"),
        ({"entitlement": "asdf"}, "is not valid"),
        ({"entitlement_pattern": "asdf"}, "is not valid"),
        ({"entitlement_pattern": "asdf", "group": 123}, "is not of type 'string'"),
        (
            {
                "entitlement": "some-entitlement",
                "entitlement_pattern": "asdf",
                "group": "some-group",
            },
            "is valid under each of",
        ),
    ],
)
def test_validate_invalid_authorization_rule(rule, message):
    config = {
        **default_config(),
        "OIDC_AUTHORIZATION_RULES": [rule],
    }
    with pytest.raises(jsonschema.ValidationError) as e:
        jsonschema.validate(config, CONFIG_SCHEMA)
    assert message in e.value.message
