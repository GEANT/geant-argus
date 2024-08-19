import jsonschema
from geant_argus.geant_argus.metadata.schema import METADATA_SCHEMAS


def validate(payload):
    schema = METADATA_SCHEMAS[payload["metadata"]["version"]]
    jsonschema.validate(payload["metadata"], schema)


def test_link_alarm_none_fields():
    metadata = {
        "version": "v0a4",
        "phase": "FINALIZED",
        "severity": "MAJOR",
        "endpoints": {
            "bgp": [],
            "link": [
                {
                    "name": "endpoint",
                    "events": [
                        {
                            "init_time": "start",
                            "clear_time": None,
                            "is_up": False,
                            "properties": {
                                "id": 15391480,
                                "equipment_name": "rt1.mar.fr.geant.net",
                                "interface_name": "et-4/1/5",
                                "snmp_trap_oid": "IF-MIB::linkDown",
                                "admin_status": None,
                                "admin_down_time": None,
                                "admin_up_time": None,
                                "oper_status": None,
                                "oper_down_time": None,
                                "oper_up_time": None,
                            },
                        }
                    ],
                }
            ],
            "coriant": [],
            "infinera": [],
        },
        "description": "",
    }
    validate({"metadata": metadata})
