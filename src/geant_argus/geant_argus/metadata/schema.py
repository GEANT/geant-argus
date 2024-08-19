METADATA_V0A3_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "definitions": {
        "event-type": {
            "type": "string",
            "enum": ["BGP", "Link", "Optical (Coriant)", "Optical (Infinera)"],
        },
        "endpoint-event": {
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
METADATA_V0A4_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "definitions": {
        "endpoint": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "events": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/endpoint_event"},
                },
            },
            "additionalProperties": False,
        },
        "up_down_null": {
            "anyOf": [{"type": "null"}, {"type": ["string"], "enum": ["up", "down"]}]
        },
        "endpoint_event": {
            "type": "object",
            "properties": {
                "init_time": {"type": "string"},
                "clear_time": {"type": ["string", "null"]},
                "is_up": {"type": "boolean"},
                "properties": {
                    "type": "object",
                    "anyOf": [
                        {"$ref": "#/definitions/bgp_properties"},
                        {"$ref": "#/definitions/link_properties"},
                        {"$ref": "#/definitions/coriant_properties"},
                        {"$ref": "#/definitions/infinera_properties"},
                    ],
                },
            },
            "required": ["init_time", "clear_time", "is_up", "properties"],
        },
        "bgp_properties": {
            "properties": {
                "id": {"type": "integer"},
                "peer": {"type": "string"},
                "status": {"type": "string"},
                "idle_time": {"type": ["string", "null"]},
                "connect_time": {"type": ["string", "null"]},
                "establish_time": {"type": ["string", "null"]},
                "source_ip": {"type": "string"},
                "equipment_name": {"type": "string"},
                "snmp_trap_oid": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "link_properties": {
            "properties": {
                "id": {"type": "integer"},
                "admin_status": {"$ref": "#/definitions/up_down_null"},
                "oper_status": {"$ref": "#/definitions/up_down_null"},
                "admin_down_time": {"type": ["string", "null"]},
                "oper_down_time": {"type": ["string", "null"]},
                "admin_up_time": {"type": ["string", "null"]},
                "oper_up_time": {"type": ["string", "null"]},
                "equipment_name": {"type": "string"},
                "interface_name": {"type": "string"},
                "snmp_trap_oid": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "coriant_properties": {
            "properties": {
                "id": {"type": "integer"},
                "status": {"type": "string"},
                "equipment_name": {"type": "string"},
                "entity_string": {"type": "string"},
                "probable_cause": {"type": "string"},
                "severity": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "infinera_properties": {
            "properties": {
                "id": {"type": "integer"},
                "status": {"type": "string"},
                "equipment_name": {"type": "string"},
                "object_name": {"type": "string"},
                "object_type": {"type": "string"},
                "probable_cause": {"type": "string"},
                "severity": {"type": "string"},
            },
            "required": ["object_type"],
            "additionalProperties": False,
        },
    },
    "properties": {
        "version": {"const": "v0a4"},
        "phase": {"type": "string"},
        "status": {"type": "string", "enum": ["ACTIVE", "CLEAR", "CLOSED"]},
        "severity": {"type": "string"},
        "endpoints": {
            "type": "object",
            "properties": {
                "bgp": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/endpoint"},
                },
                "link": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/endpoint"},
                },
                "coriant": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/endpoint"},
                },
                "infinera": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/endpoint"},
                },
            },
            "required": ["bgp", "link", "coriant", "infinera"],
            "additionalProperties": False,
        },
        "description": {"type": "string"},
        "coalesce_count": {"type": "integer"},
        "endpoint_count": {"type": "integer"},
        "short_lived": {"type": "boolean"},
    },
    "required": [
        "version",
        "phase",
        "severity",
        "endpoints",
        "description",
    ],
}

METADATA_SCHEMAS = {
    "v0a3": METADATA_V0A3_SCHEMA,
    "v0a4": METADATA_V0A4_SCHEMA,
}
