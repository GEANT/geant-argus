METADATA_V0A2_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "version": {"const": "v0a2"},
        "phase": {"type": "string"},
        "services": {"type": "object"},
        "severity": {"type": "string"},
        "endpoints": {
            "type": "object",
            "properties": {
                "juniper": {"type": "array", "items": {"type": "object"}},
                "coriant": {"type": "array", "items": {"type": "object"}},
                "infinera": {"type": "array", "items": {"type": "object"}},
            },
        },
        "description": {"type": "string"},
        "coalesce-count": {"type": "integer"},
        "endpoint-count": {"type": "integer "},
    },
    "required": [
        "phase",
        "version",
        "services",
        "severity",
        "endpoints",
        "description",
        "coalesce-count",
        "endpoint-count",
    ],
}

METADATA_V0A3_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "definitions": {
        "alarm-type": {
            "type": "string",
            "enum": ["BGP", "Link", "Optical (Coriant)", "Optical (Infinera)"],
        },
        "endpoint-alarm": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "init_time": {"type": "string"},
                "clear_time": {"type": "string"},
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
                    "type": {"$ref": "#/definitions/alarm-type"},
                    "alarm": {
                        {
                            "type": "array",
                            "items": {"$ref": "#/definitions/endpoint-alarm"},
                        }
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
