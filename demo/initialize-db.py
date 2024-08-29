import json
import pathlib
from django.core.management import call_command
from django.db import connection
import os
from argus.incident.models import create_fake_incident
from geant_argus.geant_argus.incidents.severity import IncidentSeverity

DIR = pathlib.Path(__file__).parent


def level_from_severity(severity, max_level=5) -> int:
    """
    Translate a Alarm severity to Argus incident level, AlarmSeverity 1 means lowest
    severity while Incident level 1 means highest level

    :param max_level: The maximum incident level that Argus supports (Default: 5)

    :return: Argus incident level between 1 and `max_level` (inclusive)
    """

    return min(len(IncidentSeverity) + 1 - IncidentSeverity[severity], max_level)


def purge_db():
    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE")
        cursor.execute("CREATE SCHEMA public")
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {os.environ['PGUSER']}")
        cursor.execute("GRANT ALL ON SCHEMA public TO public")


def populate_db(incidents_dir: pathlib.Path):
    for file in incidents_dir.glob("*.json"):
        data = json.loads(file.read_text())
        create_fake_incident(
            description=data["description"],
            level=IncidentSeverity[data["severity"]],
            metadata=data,
        )


if __name__ == "__main__":
    purge_db()
    call_command("migrate")
