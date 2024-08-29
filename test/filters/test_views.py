import jsonschema
import pytest
from geant_argus.geant_argus.filters.schema import FILTER_SCHEMA_V1
from geant_argus.geant_argus.filters.views import parse_filter_form_data


@pytest.mark.parametrize(
    "form_data, expected",
    [
        (
            {"field": "description", "op": "equals", "val": "some value"},
            {
                "version": "v1",
                "type": "rule",
                "field": "description",
                "operator": "contains",
                "value": "some value",
            },
        ),
        (
            {
                "op": "and",
                "0_field": "description",
                "0_op": "equals",
                "0_val": "some value",
                "1_field": "location",
                "1_op": "equals",
                "1_val": "other value",
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
                        "operator": "equals",
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
                "0_0_val": "some value",
                "1_field": "location",
                "1_op": "equals",
                "1_val": "other value",
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
                        "operator": "equals",
                        "value": "other value",
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
    ],
)
def test_parse_filter_form_data(form_data, expected):
    parsed = parse_filter_form_data(form_data)
    assert parsed == expected
    jsonschema.validate(parsed, FILTER_SCHEMA_V1)
