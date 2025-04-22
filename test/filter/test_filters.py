import jsonschema
import pytest
from geant_argus.filter.model import ComplexFilter, filter_to_text
from geant_argus.filter.schema import FILTER_SCHEMA_V1


@pytest.mark.parametrize(
    "filter_dict, text",
    [
        (
            {"type": "rule", "field": "description", "operator": "contains", "value": "something"},
            "DESCRIPTION contains 'something'",
        ),
        (
            {"type": "rule", "field": "comment", "operator": "exists", "value": "something"},
            "COMMENT exists",
        ),
        (
            {
                "type": "rule",
                "field": "description",
                "operator": "contains",
                "value": "a",
                "invert": True,
            },
            "DESCRIPTION NOT contains 'a'",
        ),
        (
            {
                "type": "rule",
                "field": "start_time",
                "operator": "before_abs",
                "value": "2025-01-01",
            },
            "START_TIME before 2025-01-01",
        ),
        (
            {
                "type": "rule",
                "field": "start_time",
                "operator": "before_rel",
                "value": 10,
                "unit": "days",
            },
            "START_TIME before 10 days ago",
        ),
        (
            {
                "type": "rule",
                "field": "start_time",
                "operator": "after_abs",
                "value": "2025-01-01",
            },
            "START_TIME after 2025-01-01",
        ),
        (
            {
                "type": "rule",
                "field": "start_time",
                "operator": "after_rel",
                "value": 10,
                "unit": "days",
            },
            "START_TIME after 10 days ago",
        ),
        (
            {"type": "group", "operator": "and", "items": []},
            "",
        ),
        (
            {
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "something",
                    }
                ],
            },
            "DESCRIPTION contains 'something'",
        ),
        (
            {
                "type": "group",
                "operator": "none",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "something",
                    }
                ],
            },
            "NOT (DESCRIPTION contains 'something')",
        ),
        (
            {
                "type": "group",
                "operator": "and",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "something",
                    },
                    {"type": "rule", "field": "ack", "operator": "exists", "value": True},
                ],
            },
            "(DESCRIPTION contains 'something' AND ACK exists)",
        ),
        (
            {
                "type": "group",
                "operator": "none",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "something",
                    },
                    {"type": "rule", "field": "ack", "operator": "exists", "value": True},
                ],
            },
            "NOT (DESCRIPTION contains 'something' OR ACK exists)",
        ),
        (
            {
                "type": "group",
                "operator": "or",
                "items": [
                    {
                        "type": "rule",
                        "field": "description",
                        "operator": "contains",
                        "value": "a",
                    },
                    {
                        "type": "group",
                        "operator": "and",
                        "items": [
                            {
                                "type": "rule",
                                "field": "description",
                                "operator": "contains",
                                "value": "b",
                            },
                            {"type": "rule", "field": "ack", "operator": "exists", "value": True},
                        ],
                    },
                ],
            },
            "(DESCRIPTION contains 'a' OR (DESCRIPTION contains 'b' AND ACK exists))",
        ),
    ],
)
def test_filter_to_text(filter_dict, text):
    filter_dict = ComplexFilter.with_version(filter_dict)
    jsonschema.validate(filter_dict, FILTER_SCHEMA_V1)
    assert filter_to_text(filter_dict) == text
