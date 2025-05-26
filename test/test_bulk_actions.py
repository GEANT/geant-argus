from django.utils import timezone
import pytest

from geant_argus.geant_argus.incidents.bulk_actions import clear_incident_in_metadata
from datetime import datetime


@pytest.fixture
def metadata():
    return {
        "phase": "FINALIZED",
        "status": "CLEAR",
        "comment": None,
        "version": "v0a5",
        "location": ["LISBON", "PDS"],
        "severity": "CRITICAL",
        "blacklist": {"applied": False},
        "endpoints": {
            "bgp": [
                {
                    "events": [
                        {
                            "is_up": False,
                            "init_time": "2024-11-05T17:09:50",
                            "clear_time": None,
                            "properties": {
                                "id": 15865744,
                                "peer": "159.226.10.14",
                                "status": "connected",
                                "idle_time": "2024-11-05T17:09:50",
                                "source_ip": "62.40.96.5",
                                "connect_time": "2024-11-05T17:09:57",
                                "snmp_trap_oid": "BGP4-MIB::bgpBackwardTransition",
                                "equipment_name": "rt1.mar.fr.geant.net",
                                "establish_time": None,
                            },
                        }
                    ],
                    "hostname": "rt1.mar.fr.geant.net",
                    "event_count": 1,
                    "remote_peer": "159.226.10.14",
                }
            ],
            "link": [
                {
                    "events": [
                        {
                            "is_up": False,
                            "init_time": "2024-11-06T15:21:35",
                            "clear_time": None,
                            "properties": {
                                "id": 15867174,
                                "oper_status": "down",
                                "admin_status": "up",
                                "oper_up_time": None,
                                "admin_up_time": "2024-11-06T15:21:35",
                                "snmp_trap_oid": "IF-MIB::linkDown",
                                "equipment_name": "mx2.lis.pt.geant.net",
                                "interface_name": "et-5/0/5",
                                "oper_down_time": "2024-11-06T15:21:35",
                                "admin_down_time": None,
                            },
                        },
                        {
                            "is_up": True,
                            "init_time": "2024-11-06T15:21:24",
                            "clear_time": "2024-11-06T15:21:25",
                            "properties": {
                                "id": 15867139,
                                "oper_status": "up",
                                "admin_status": "up",
                                "oper_up_time": "2024-11-06T15:21:25",
                                "admin_up_time": "2024-11-06T15:21:24",
                                "snmp_trap_oid": "IF-MIB::linkDown",
                                "equipment_name": "mx2.lis.pt.geant.net",
                                "interface_name": "et-5/0/5",
                                "oper_down_time": "2024-11-06T15:21:24",
                                "admin_down_time": None,
                            },
                        },
                    ],
                    "hostname": "mx2.lis.pt.geant.net",
                    "interface": "et-5/0/5",
                    "event_count": 2,
                },
            ],
            "coriant": [
                {
                    "port": "1-1.1-Optical-TTP",
                    "events": [
                        {
                            "is_up": False,
                            "init_time": "2024-11-06T15:21:37",
                            "clear_time": None,
                            "properties": {
                                "id": 124744,
                                "status": "Raised",
                                "severity": "critical",
                                "entity_string": "1-1.1-Optical-TTP",
                                "equipment_name": "MAD01-GRV1",
                                "probable_cause": "los",
                            },
                        }
                    ],
                    "ne_name": "MAD01-GRV1",
                    "event_count": 1,
                },
                {
                    "port": "1-1.4-Optical-100GbE-TTP",
                    "events": [
                        {
                            "is_up": True,
                            "init_time": "2024-11-06T15:21:37",
                            "clear_time": "2024-11-06T19:59:37",
                            "properties": {
                                "id": 124749,
                                "status": "Clear",
                                "severity": "major",
                                "entity_string": "1-1.4-Optical-100GbE-TTP",
                                "equipment_name": "MAD01-GRV1",
                                "probable_cause": "remoteFault",
                            },
                        }
                    ],
                    "ne_name": "MAD01-GRV1",
                    "event_count": 1,
                },
            ],
            "infinera": [
                {
                    "port": "2-A-1-S1-1",
                    "events": [
                        {
                            "is_up": False,
                            "init_time": "2024-11-06T20:13:16",
                            "clear_time": None,
                            "properties": {
                                "id": 221939,
                                "status": "Clear",
                                "severity": "Critical",
                                "object_name": "2-A-1-S1-1",
                                "object_type": "LOCAL_OPTICAL_SNC",
                                "equipment_name": "BOD01-MTC6-1",
                                "probable_cause": "Signaled SNC failure (COM0038)",
                            },
                        }
                    ],
                    "ne_name": "BOD01-MTC6-1",
                    "event_count": 1,
                },
                {
                    "port": "2-A-1-S1-2",
                    "events": [
                        {
                            "is_up": True,
                            "init_time": "2024-11-06T20:13:16",
                            "clear_time": "2024-11-06T20:14:55",
                            "properties": {
                                "id": 221944,
                                "status": "Clear",
                                "severity": "Critical",
                                "object_name": "2-A-1-S1-2",
                                "object_type": "LOCAL_OPTICAL_SNC",
                                "equipment_name": "BOD01-MTC6-1",
                                "probable_cause": "Signaled SNC failure (COM0038)",
                            },
                        }
                    ],
                    "ne_name": "BOD01-MTC6-1",
                    "event_count": 1,
                },
            ],
            "fiberlink": [
                {
                    "ne_a": "PDS01-MTC9-1",
                    "ne_b": "LIS01-MTC6-1",
                    "events": [
                        {
                            "is_up": False,
                            "init_time": "2024-11-06T15:21:50",
                            "clear_time": None,
                            "properties": {
                                "id": 221929,
                                "status": "Raised",
                                "severity": "Critical",
                                "object_name": "",
                                "object_type": "dstAlarmSeverity",
                                "equipment_name": "PDS01-MTC9-1/LIS01-MTC6-1",
                                "probable_cause": "unknown",
                            },
                        }
                    ],
                    "event_count": 1,
                }
            ],
        },
        "equipment": ["LIS01-MTC6-1", "PDS01-MTC9-1"],
        "init_time": "2024-11-06T15:21:51",
        "clear_time": "2024-11-06T19:59:37",
        "ticket_ref": "",
        "description": "LIS-MAD-DFROUTE Incident (BOD-GEN1-ESNET-23093-400G, LIS-MAD-IPTRUNK)",
        "short_lived": False,
        "endpoint_count": 22,
    }



def is_naive_isoformat(s):
    try:
        dt = datetime.fromisoformat(s)
        return dt.tzinfo is None
    except ValueError:
        return False

def test_clear_incident_in_metadata(metadata):
    clear_time = timezone.now().replace(tzinfo=None).isoformat()
    clear_incident_in_metadata(metadata, clear_time=clear_time)
    assert metadata["status"] == "CLEAR"
    assert metadata["clear_time"] == clear_time

    endpoints = metadata["endpoints"]
    assert endpoints["bgp"][0]["events"][0]["is_up"] is True
    assert endpoints["bgp"][0]["events"][0]["clear_time"] == clear_time
    assert endpoints["bgp"][0]["events"][0]["properties"]["establish_time"] == clear_time
    assert endpoints["bgp"][0]["events"][0]["properties"]["status"] == "established"

    assert endpoints["link"][0]["events"][0]["is_up"] is True
    assert endpoints["link"][0]["events"][0]["clear_time"] == clear_time
    assert endpoints["link"][0]["events"][0]["properties"]["oper_up_time"] == clear_time
    assert endpoints["link"][0]["events"][0]["properties"]["oper_up_time"] == clear_time
    assert is_naive_isoformat(endpoints["link"][0]["events"][0]["clear_time"])

    assert endpoints["link"][0]["events"][1]["clear_time"] != clear_time
    assert endpoints["link"][0]["events"][1]["properties"]["oper_up_time"] != clear_time

    assert endpoints["coriant"][0]["events"][0]["is_up"] is True
    assert endpoints["coriant"][0]["events"][0]["clear_time"] == clear_time
    assert endpoints["coriant"][0]["events"][0]["properties"]["status"] == "Clear"

    assert endpoints["coriant"][1]["events"][0]["clear_time"] != clear_time

    assert endpoints["infinera"][0]["events"][0]["is_up"] is True
    assert endpoints["infinera"][0]["events"][0]["clear_time"] == clear_time
    assert endpoints["infinera"][0]["events"][0]["properties"]["status"] == "Clear"
    assert endpoints["infinera"][1]["events"][0]["clear_time"] != clear_time

    assert endpoints["fiberlink"][0]["events"][0]["is_up"] is True
    assert endpoints["fiberlink"][0]["events"][0]["clear_time"] == clear_time
    assert endpoints["fiberlink"][0]["events"][0]["properties"]["status"] == "Clear"
