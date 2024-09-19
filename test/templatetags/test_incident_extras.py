import dataclasses

import pytest

from geant_argus.geant_argus.incidents.severity import IncidentSeverity
from geant_argus.geant_argus.templatetags.incident_extras import blacklist_symbol, level_to_badge


@dataclasses.dataclass
class FakeIncident:
    level: int
    open: bool = True
    metadata: dict = dataclasses.field(default_factory=dict)


@pytest.mark.parametrize(
    "incident, expected_classes",
    [
        (FakeIncident(level=1), "incident-critical"),
        (FakeIncident(level=1, open=False), "incident-critical incident-closed"),
        (FakeIncident(level=2), "incident-major"),
        (FakeIncident(level=3), "incident-minor"),
        (FakeIncident(level=4), "incident-default"),
        (FakeIncident(level=5), "incident-default"),
    ],
)
def test_level_to_badge(incident, expected_classes):
    assert level_to_badge(incident) == expected_classes


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
