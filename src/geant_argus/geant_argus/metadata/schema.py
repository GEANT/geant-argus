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
