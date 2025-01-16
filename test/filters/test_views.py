import jsonschema
import pytest
from geant_argus.geant_argus.filters.schema import FILTER_SCHEMA_V1
from geant_argus.geant_argus.filters.views import parse_filter_form_data, update_filter


@pytest.mark.parametrize(
    "form_data, expected",
    [
        (
            {"field": "description", "op": "equals", "val:str": "some value"},
            {
                "version": "v1",
                "type": "rule",
                "field": "description",
                "operator": "contains",
                "value": "some value",
            },
        ),
        (
            {"field": "description", "op": "contains", "val:str": "some value", "invert": "on"},
            {
                "version": "v1",
                "type": "rule",
                "invert": True,
                "field": "description",
                "operator": "contains",
                "value": "some value",
            },
        ),
        (
            {"field": "ack", "op": "exists", "val:bool": "true", "invert": "on"},
            {
                "version": "v1",
                "type": "rule",
                "field": "ack",
                "operator": "exists",
                "invert": True,
                "value": True,
            },
        ),
        (
            {
                "op": "and",
                "0_field": "description",
                "0_op": "equals",
                "0_val:str": "some value",
                "1_field": "location",
                "1_op": "contains",
                "1_val:str": "other value",
            },
            {
                "version": "v1",
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "some value",
                    },
                    {
                        "type": "rule",
                        "field": "location",
                        "operator": "contains",
                        "value": "other value",
                    },
                ],
            },
        ),
        (
            {
                "op": "and",
                "0_op": "or",
                "0_0_field": "description",
                "0_0_op": "equals",
                "0_0_val:str": "some value",
                "1_field": "location",
                "1_op": "contains",
                "1_invert": "on",
                "1_val:str": "other value",
            },
            {
                "version": "v1",
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "group",
                        "operator": "or",
                        "items": [
                            {
                                "type": "rule",
                                "field": "description",
                                "operator": "contains",
                                "value": "some value",
                            },
                        ],
                    },
                    {
                        "type": "rule",
                        "field": "location",
                        "operator": "contains",
                        "value": "other value",
                        "invert": True,
                    },
                ],
            },
        ),
        (
            {
                "op": "equals",
                "field": "and",
                "val": "equals",
            },
            {
                "version": "v1",
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "",
                    }
                ],
            },
        ),
        (
            {
                "op": "none",
                "0_field": "location",
                "0_op": "contains",
                "0_val:str": "other value",
            },
            {
                "version": "v1",
                "type": "group",
                "operator": "none",
                "items": [
                    {
                        "type": "rule",
                        "field": "location",
                        "operator": "contains",
                        "value": "other value",
                    },
                ],
            },
        ),
        (
            {
                "op": "is",
                "field": "short_lived",
                "val:bool": "true",
            },
            {
                "version": "v1",
                "type": "rule",
                "operator": "is",
                "value": True,
                "field": "short_lived",
            },
        ),
    ],
)
def test_parse_filter_form_data(form_data, expected):
    parsed = parse_filter_form_data(form_data)
    assert parsed == expected
    jsonschema.validate(parsed, FILTER_SCHEMA_V1)


@pytest.mark.parametrize(
    "filter_dict, command, expected",
    [
        (
            {
                "version": "v1",
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "",
                    }
                ],
            },
            {"create_after": "0_"},
            {
                "version": "v1",
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "",
                    },
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "",
                    },
                ],
            },
        ),
        (
            {
                "version": "v1",
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "1",
                    },
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "2",
                    },
                ],
            },
            {"move_up": "1_"},
            {
                "version": "v1",
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "2",
                    },
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "1",
                    },
                ],
            },
        ),
        (
            {
                "type": "rule",
                "field": "description",
                "operator": "contains",
                "value": "1",
            },
            {"create_after": "root"},
            {
                "version": "v1",
                "type": "group",
                "operator": "or",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "1",
                    },
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "",
                    },
                ],
            },
        ),
    ],
)
def test_update_filter(filter_dict, command, expected):
    assert update_filter(filter_dict, command) == expected
