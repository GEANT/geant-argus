import dataclasses

import pytest

from geant_argus.geant_argus.templatetags.incident_extras import level_to_badge


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
