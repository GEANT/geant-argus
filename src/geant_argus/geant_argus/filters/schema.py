METADATA_V0A3_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "definitions": {
        "filter-rule": {
            "type": "object",
            "properties": {
                "type": {
                    "const": "rule",
                    "operator": "string",
                    "field": "string",
                    "value": "string",
                }
            },
        },
        "filter-group": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "init_time": {"type": "string"},
                "clear_time": {"type": ["string", "null"]},
                "is_up": {"type": "boolean"},
                "properties": {"type": "object"},
            },
        },
    },
    "properties": {
        "version": {"const": "v0a3"},
        "phase": {"type": "string"},
        "severity": {"type": "string"},
        "endpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"$ref": "#/definitions/event-type"},
                    "alarms": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/endpoint-event"},
                    },
                },
            },
        },
        "description": {"type": "string"},
        "coalesce-count": {"type": "integer"},
    },
    "required": [
        "phase",
        "version",
        "severity",
        "endpoints",
        "description",
        "coalesce-count",
    ],
}
