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
                "status": {"type": ["string", "null"]},
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
        "blacklist_info": {
            "type": "object",
            "properties": {
                "applied": {"type": "boolean"},
                "message": {"type": "string"},
                "original_severity": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    "properties": {
        "version": {"const": "v0a4"},
        "init_time": {"type": ["string", "null"]},
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
        "blacklist": {"$ref": "#/definitions/blacklist_info"},
        "short_lived": {"type": "boolean"},
    },
    "required": [
        "version",
        "phase",
        "severity",
        "blacklist",
        "endpoints",
        "description",
    ],
}


def v0a5_endpoint_event(props):
    return {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "init_time": {"type": "string"},
                "clear_time": {"type": ["string", "null"]},
                "is_up": {"type": "boolean"},
                "properties": {
                    "type": "object",
                    "properties": props,
                    "additionalProperties": False,
                },
            },
            "required": ["init_time", "clear_time", "is_up", "properties"],
        },
    }


METADATA_V0A5_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "definitions": {
        "bgp_endpoint": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string"},
                "remote_peer": {"type": "string"},
                "events": v0a5_endpoint_event(
                    {
                        "id": {"type": "integer"},
                        "peer": {"type": ["string", "null"]},
                        "status": {"type": ["string", "null"]},
                        "idle_time": {"type": ["string", "null"]},
                        "connect_time": {"type": ["string", "null"]},
                        "establish_time": {"type": ["string", "null"]},
                        "source_ip": {"type": ["string", "null"]},
                        "equipment_name": {"type": ["string", "null"]},
                        "snmp_trap_oid": {"type": ["string", "null"]},
                    }
                ),
            },
        },
        "link_endpoint": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string"},
                "interface": {"type": "string"},
                "events": v0a5_endpoint_event(
                    {
                        "id": {"type": "integer"},
                        "admin_status": {
                            "anyOf": [
                                {"type": "null"},
                                {"type": ["string"], "enum": ["up", "down"]},
                            ]
                        },
                        "oper_status": {
                            "anyOf": [
                                {"type": "null"},
                                {"type": ["string"], "enum": ["up", "down"]},
                            ]
                        },
                        "admin_down_time": {"type": ["string", "null"]},
                        "oper_down_time": {"type": ["string", "null"]},
                        "admin_up_time": {"type": ["string", "null"]},
                        "oper_up_time": {"type": ["string", "null"]},
                        "equipment_name": {"type": ["string", "null"]},
                        "interface_name": {"type": ["string", "null"]},
                        "snmp_trap_oid": {"type": ["string", "null"]},
                    }
                ),
            },
        },
        "coriant_endpoint": {
            "type": "object",
            "properties": {
                "ne_name": {"type": "string"},
                "port": {"type": "string"},
                "events": v0a5_endpoint_event(
                    {
                        "id": {"type": "integer"},
                        "status": {"type": "string"},
                        "equipment_name": {"type": ["string", "null"]},
                        "entity_string": {"type": ["string", "null"]},
                        "probable_cause": {"type": ["string", "null"]},
                        "severity": {"type": ["string", "null"]},
                    }
                ),
            },
        },
        "infinera_endpoint": {
            "type": "object",
            "properties": {
                "ne_name": {"type": "string"},
                "port": {"type": "string"},
                "events": v0a5_endpoint_event(
                    {
                        "id": {"type": "integer"},
                        "status": {"type": ["string", "null"]},
                        "equipment_name": {"type": ["string", "null"]},
                        "object_name": {"type": ["string", "null"]},
                        "object_type": {"type": ["string", "null"]},
                        "probable_cause": {"type": ["string", "null"]},
                        "severity": {"type": ["string", "null"]},
                    }
                ),
            },
        },
        "blacklist_info": {
            "type": "object",
            "properties": {
                "applied": {"type": "boolean"},
                "message": {"type": "string"},
                "original_severity": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    "properties": {
        "version": {"const": "v0a5"},
        "init_time": {"type": ["string", "null"]},
        "clear_time": {"type": ["string", "null"]},
        "blacklist": {"$ref": "#/definitions/blacklist_info"},
        "phase": {"type": "string"},
        "status": {"type": "string", "enum": ["ACTIVE", "CLEAR", "CLOSED"]},
        "severity": {"type": "string"},
        "location": {"type": "array", "items": {"type": "string"}},
        "equipment": {"type": "array", "items": {"type": "string"}},
        "endpoint_count": {"type": "integer"},
        "ticket_ref": {"type": "string"},
        "endpoints": {
            "type": "object",
            "properties": {
                "bgp": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/bgp_endpoint"},
                },
                "link": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/link_endpoint"},
                },
                "coriant": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/coriant_endpoint"},
                },
                "infinera": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/infinera_endpoint"},
                },
            },
            "required": ["bgp", "link", "coriant", "infinera"],
            "additionalProperties": False,
        },
        "description": {"type": "string"},
        "short_lived": {"type": "boolean"},
        "comment": {"type": ["string", "null"]},
    },
    "required": [
        "version",
        "phase",
        "status",
        "severity",
        "endpoints",
        "description",
        "short_lived",
        "blacklist",
        "endpoint_count",
    ],
}

METADATA_SCHEMAS = {
    "v0a3": METADATA_V0A3_SCHEMA,
    "v0a4": METADATA_V0A4_SCHEMA,
    "v0a5": METADATA_V0A5_SCHEMA,
}
