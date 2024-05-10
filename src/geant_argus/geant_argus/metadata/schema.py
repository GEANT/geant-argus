METADATA_V0A1_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "definitions": {
        "endpoint": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "events": {
                    "type": "array",
                    "items": {"type": "object"},
                },
            },
            "required": ["name", "events"],
        },
    },
    "type": "object",
    "properties": {
        "version": {"const": "v0a1"},
        "endpoints": {
            "type": "array",
            "items": {"$ref": "#/definitions/endpoint"},
        },
    },
    "required": ["version", "endpoints"],
}
