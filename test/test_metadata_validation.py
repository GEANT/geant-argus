import jsonschema
import pytest
from geant_argus.geant_argus.metadata.schema import METADATA_SCHEMAS


def validate(payload):
    schema = METADATA_SCHEMAS[payload["metadata"]["version"]]
    jsonschema.validate(payload["metadata"], schema)


@pytest.mark.parametrize("version", ["v0a5", "v1"])
def test_link_alarm_none_fields(version):
    metadata = {
        "version": version,
        "phase": "FINALIZED",
        "severity": "MEDIUM",
        "status": "ACTIVE",
        "comment": "",
        "short_lived": False,
        "endpoint_count": 1,
        "endpoints": {
            "bgp": [],
            "link": [
                {
                    "name": "endpoint",
                    "hostname": "some host",
                    "interface": "ifc",
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
        "blacklist": {"applied": False},
    }
    validate({"metadata": metadata})
