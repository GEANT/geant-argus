import dataclasses
import datetime

import pytest

from geant_argus.geant_argus.incidents.severity import IncidentSeverity
from geant_argus.geant_argus.templatetags.incident_extras import (
    blacklist_symbol,
    incident_level_to_badge,
    incident_status,
)


@dataclasses.dataclass
class FakeIncident:
    level: int = 1
    open: bool = True
    metadata: dict = dataclasses.field(default_factory=dict)


@pytest.mark.parametrize(
    "incident, expected_classes",
    [
        (FakeIncident(level=1), "incident-critical border-base-content"),
        (
            FakeIncident(level=1, metadata={"status": "CLOSED"}),
            "incident-critical incident-closed border-base-content/50",
        ),
        (FakeIncident(level=2), "incident-major border-base-content"),
        (FakeIncident(level=3), "incident-minor border-base-content"),
        (FakeIncident(level=4), "incident-default border-base-content"),
        (FakeIncident(level=5), "incident-default border-base-content"),
    ],
)
def test_level_to_badge(incident, expected_classes):
    assert incident_level_to_badge(incident) == expected_classes


@pytest.mark.parametrize(
    "original_severity, final_severity, symbol",
    [
        ("CRITICAL", "MINOR", "▼"),
        ("MAJOR", "MAJOR", "="),
        ("MAJOR", "CRITICAL", "▲"),
        (None, "MINOR", "?"),
    ],
)
def test_blacklist_symbol(original_severity, final_severity, symbol):
    incident = FakeIncident(
        level=IncidentSeverity[final_severity],
        metadata={"blacklist": {"original_severity": original_severity}},
    )
    assert blacklist_symbol(incident) == symbol


NOW = datetime.datetime.now()
JUST_YET = NOW - datetime.timedelta(seconds=10)
A_WHILE_AGO = NOW - datetime.timedelta(minutes=2)


@pytest.mark.parametrize(
    "incident, expected_status",
    [
        (FakeIncident(metadata={"phase": "FINALIZED"}), "Active"),
        (FakeIncident(metadata={"phase": "FINALIZED", "clearing_since": None}), "Active"),
        (FakeIncident(metadata={"phase": "FINALIZED", "clearing_since": JUST_YET}), "Active"),
        (FakeIncident(metadata={"phase": "FINALIZED", "clearing_since": A_WHILE_AGO}), "Stuck"),
        (FakeIncident(metadata={"phase": "PENDING", "clearing_since": A_WHILE_AGO}), "Active"),
        (
            FakeIncident(
                metadata={"phase": "FINALIZED", "status": "CLEAR", "clearing_since": A_WHILE_AGO}
            ),
            "Clear",
        ),
    ],
)
def test_stuck_incident(incident, expected_status):
    assert incident_status(incident) == expected_status
