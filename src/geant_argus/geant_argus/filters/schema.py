FILTER_SCHEMA_V1 = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "definitions": {
        "filter-rule": {
            "type": "object",
            "properties": {
                "type": {"const": "rule"},
                "field": {"type": "string"},
                "invert": {"type": "boolean"},
                "operator": {"type": "string"},
                "value": {"type": ["string", "boolean", "number"]},
                "unit": {"type": "string", "enum": ["minutes", "hours", "days", "weeks"]},
            },
            "required": ["type", "field", "operator", "value"],
        },
        "filter-group": {
            "type": "object",
            "properties": {
                "type": {"const": "group"},
                "operator": {"type": "string", "enum": ["and", "or", "none"]},
                "items": {
                    "type": "array",
                    "items": {
                        "anyOf": [
                            {"$ref": "#/definitions/filter-rule"},
                            {"$ref": "#/definitions/filter-group"},
                        ]
                    },
                },
            },
            "required": ["type", "operator", "items"],
        },
    },
    "properties": {
        "version": {"const": "v1"},
    },
    "anyOf": [
        {"$ref": "#/definitions/filter-group"},
        {"$ref": "#/definitions/filter-rule"},
    ],
    "required": ["version"],
}
