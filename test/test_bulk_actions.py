from django.utils import timezone
import pytest

from geant_argus.geant_argus.incidents.bulk_actions import clear_incident_in_metadata
from unittest.mock import patch, MagicMock
from geant_argus.geant_argus.incidents.bulk_actions import (
    bulk_clear_incidents,
    bulk_close_incidents,
    bulk_update_ticket_ref,
)
from django.test.client import RequestFactory
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware


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


def test_clear_incident_in_metadata(metadata):
    clear_time = timezone.now().isoformat()
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


@pytest.mark.django_db
@patch("geant_argus.geant_argus.incidents.bulk_actions.clear_alarm")
def test_bulk_clear_incidents(mock_clear_alarm, default_user):
    request = RequestFactory().get("/foo")
    request.user = default_user
    qs = [MagicMock(metadata={"status": "ACTIVE", "endpoints": {}})]
    data = {"timestamp": timezone.now()}
    clear_time = data["timestamp"].replace(tzinfo=None).isoformat()
    mock_clear_alarm.return_value = None

    incidents = bulk_clear_incidents(request, qs, data)

    assert len(incidents) == 1
    assert incidents[0].metadata["status"] == "CLEAR"
    assert incidents[0].metadata["clear_time"] == clear_time
    assert mock_clear_alarm.call_args == ((qs[0].source_incident_id, {"clear_time": clear_time}),)
    assert mock_clear_alarm.call_count == 1
    assert qs[0].save.call_count == 1


def bulk_close_incidents_mock_qs():
    mock_incidents = MagicMock(
        metadata={"status": "ACTIVE", "endpoints": {}}, source_incident_id=12345
    )
    mock_events = MagicMock()
    mock_events.incident = mock_incidents
    mock_qs = MagicMock()
    mock_qs.close.return_value = [mock_events]
    return mock_qs


@pytest.mark.parametrize(
    "status_code, expected_message_template",
    [
        (
            # Custom message
            400,
            "API error while {message} with ID 12345: "
            "Bad request, alarm may be pending (HTTP 400)",
        ),
        (
            # No custom message
            418,
            "API error while {message} with ID 12345: "
            "Server refuses to brew coffee because it is a teapot. (HTTP 418)",
        ),
    ],
)
@pytest.mark.parametrize(
    "mock_qs, bulk_func, custom_message",
    [
        (bulk_close_incidents_mock_qs(), bulk_close_incidents, "closing incident"),
        (
            [MagicMock(metadata={"status": "ACTIVE", "endpoints": {}}, source_incident_id=12345)],
            bulk_clear_incidents,
            "clearing incident",
        ),
        (
            [MagicMock(metadata={"status": "ACTIVE", "endpoints": {}}, source_incident_id=12345)],
            bulk_update_ticket_ref,
            "updating ticket_ref for incident",
        ),
    ],
)
@pytest.mark.django_db
@patch("requests.request")
def test_bulk_action_messages(
    mock_request,
    default_user,
    settings,
    mock_qs,
    bulk_func,
    custom_message,
    status_code,
    expected_message_template,
):
    settings.DASHBOARD_ALARMS_DISABLE_SYNCHRONIZATION = 0
    settings.DASHBOARD_ALARMS_API_URL = "doesnt matter"
    request = RequestFactory().get("/foo")
    SessionMiddleware(lambda x: x).process_request(request)
    MessageMiddleware(lambda x: x).process_request(request)
    request.user = default_user

    data = {"timestamp": timezone.now(), "ticket_ref": "1234"}
    mock_request.return_value = MagicMock()
    mock_request.return_value.status_code = status_code

    incidents = bulk_func(request, mock_qs, data)

    messages = list(get_messages(request))
    assert len(messages) == 1
    assert messages[0].message == expected_message_template.format(message=custom_message)
    assert len(incidents) == 0
