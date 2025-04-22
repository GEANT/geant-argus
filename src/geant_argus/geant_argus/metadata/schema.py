import copy


def v1_endpoint_event(props):
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


METADATA_V1_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "definitions": {
        "bgp_endpoint": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string"},
                "remote_peer": {"type": "string"},
                "has_more_events": {"type": ["boolean", "null"]},
                "event_count": {"type": "number"},
                "events": v1_endpoint_event(
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
            "required": ["hostname", "remote_peer", "events"],
        },
        "link_endpoint": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string"},
                "interface": {"type": "string"},
                "has_more_events": {"type": ["boolean", "null"]},
                "event_count": {"type": "number"},
                "events": v1_endpoint_event(
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
            "required": ["hostname", "interface", "events"],
        },
        "coriant_endpoint": {
            "type": "object",
            "properties": {
                "ne_name": {"type": "string"},
                "port": {"type": "string"},
                "has_more_events": {"type": ["boolean", "null"]},
                "event_count": {"type": "number"},
                "events": v1_endpoint_event(
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
            "required": ["ne_name", "port", "events"],
        },
        "infinera_endpoint": {
            "type": "object",
            "properties": {
                "ne_name": {"type": "string"},
                "port": {"type": "string"},
                "has_more_events": {"type": ["boolean", "null"]},
                "event_count": {"type": "number"},
                "events": v1_endpoint_event(
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
            "required": ["ne_name", "port", "events"],
        },
        "fiberlink_endpoint": {
            "type": "object",
            "properties": {
                "ne_a": {"type": "string"},
                "ne_b": {"type": "string"},
                "has_more_events": {"type": ["boolean", "null"]},
                "event_count": {"type": "number"},
                "events": v1_endpoint_event(
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
            "required": ["ne_a", "ne_b", "events"],
        },
        "blacklist_info": {
            "type": "object",
            "properties": {
                "applied": {"type": "boolean"},
                "message": {"type": "string"},
                "original_severity": {"type": "string"},
            },
        },
    },
    "properties": {
        "version": {"const": "v1"},
        "dirty": {"type": "boolean"},
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
                "fiberlink": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/fiberlink_endpoint"},
                },
            },
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
        "comment",  # comment is required for filtering to work properly
    ],
}

METADATA_V0A5_SCHEMA = copy.deepcopy(METADATA_V1_SCHEMA)
METADATA_V0A5_SCHEMA["properties"]["version"]["const"] = "v0a5"
METADATA_SCHEMAS = {
    "v0a5": METADATA_V0A5_SCHEMA,
    "v1": METADATA_V1_SCHEMA,
}
