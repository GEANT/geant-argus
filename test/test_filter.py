import pytest
from geant_argus.geant_argus.filters.views import parse_filter_form_data


@pytest.mark.parametrize(
    "form_data, expected",
    [
        (
            {"field": "some field", "op": "eq", "val": "some value"},
            {
                "type": "rule",
                "field": "some field",
                "operator": "eq",
                "value": "some value",
            },
        ),
        (
            {
                "op": "and",
                "0_field": "some field",
                "0_op": "eq",
                "0_val": "some value",
                "1_field": "other field",
                "1_op": "eq",
                "1_val": "other value",
            },
            {
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "some field",
                        "operator": "eq",
                        "value": "some value",
                    },
                    {
                        "type": "rule",
                        "field": "other field",
                        "operator": "eq",
                        "value": "other value",
                    },
                ],
            },
        ),
        (
            {
                "op": "and",
                "0_op": "or",
                "0_0_field": "some field",
                "0_0_op": "eq",
                "0_0_val": "some value",
                "1_field": "other field",
                "1_op": "eq",
                "1_val": "other value",
            },
            {
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "group",
                        "operator": "or",
                        "items": [
                            {
                                "type": "rule",
                                "field": "some field",
                                "operator": "eq",
                                "value": "some value",
                            },
                        ],
                    },
                    {
                        "type": "rule",
                        "field": "other field",
                        "operator": "eq",
                        "value": "other value",
                    },
                ],
            },
        ),
    ],
)
def test_parse_filter_form_data(form_data, expected):
    assert parse_filter_form_data(form_data) == expected


def test_parse_filter_form_data2():
    form_data = {
        "0": "and",
        "0_0": "or",
        "0_0_0_field": "some field",
        "0_0_0_op": "eq",
        "0_0_0_val": "some value",
    }
    expected = {
        "type": "group",
        "operator": "and",
        "items": [
            {
                "type": "group",
                "operator": "or",
                "items": [{"field": "somefield", "operator": "eq", "value": "some value"}],
            }
        ],
    }
    assert parse_filter_form_data(form_data) == expected
