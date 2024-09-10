FILTER_SCHEMA_V1 = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "definitions": {
        "filter-rule": {
            "type": "object",
            "properties": {
                "type": {"const": "rule"},
                "field": {"type": "string"},
                "operator": {"type": "string"},
                "value": {"type": "string"},
                "unit": {"type": "string"},
            },
            "required": ["type", "field", "operator", "value"],
        },
        "filter-group": {
            "type": "object",
            "properties": {
                "type": {"const": "group"},
                "operator": {"type": "string", "enum": ["and", "or"]},
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
        {"$ref": "#/definitions/filter-rule"},
        {"$ref": "#/definitions/filter-group"},
    ],
    "required": ["version"],
}
