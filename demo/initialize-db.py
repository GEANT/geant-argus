#! /usr/bin/env python3
import datetime
import json
import os
import pathlib
import sys

import django
from django.core.management import call_command
from django.db import connection

from geant_argus.geant_argus.incidents.severity import IncidentSeverity
from geant_argus.geant_argus.metadata.validation import validate_metadata

DIR = pathlib.Path(__file__).parent
INITIALIZED_SENTINEL_SCHEMA = "initialized_sentinel"


def get_pguser():
    for key in ("PGUSER", "POSTGRES_USER"):
        if key in os.environ:
            return os.environ[key]
    raise ValueError(
        "Could not determine postgres user, please set either the PGUSER or POSTGRES_USER "
        "environment variable"
    )


def is_initialized():
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata")
        all_schemas = list(r[0] for r in cursor.fetchall())
        return INITIALIZED_SENTINEL_SCHEMA in all_schemas


def purge_db():
    with connection.cursor() as cursor:
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE")
        cursor.execute("CREATE SCHEMA public")
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {get_pguser()}")
        cursor.execute("GRANT ALL ON SCHEMA public TO public")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {INITIALIZED_SENTINEL_SCHEMA}")


def populate_db(incidents_dir: pathlib.Path):
    for file in incidents_dir.glob("*.json"):
        metadata = json.loads(file.read_text())
        error = validate_metadata(metadata)
        if error:
            print(f"skipping {str(file)} due to schema error: '{error}'")
            continue
        create_fake_incident(metadata)
        print(f"Created fake incident {metadata['description']}")


def create_fake_incident(metadata=None):
    from argus.incident.models import get_or_create_default_instances, Incident
    from argus.util.datetime_utils import INFINITY_REPR
    from django.utils import timezone
    from random import randint

    user, _, source_system = get_or_create_default_instances()

    description = metadata["description"]
    level = IncidentSeverity[metadata["severity"]]
    if init_time := metadata.get("init_time"):
        start_time = datetime.datetime.fromisoformat(init_time).replace(
            tzinfo=timezone.get_default_timezone()
        )
    else:
        start_time = timezone.now()

    ticket_url = metadata.pop("ticket_url", "")
    end_time = INFINITY_REPR
    source_incident_id = randint(1, 10**6) + 10**7
    incident = Incident.objects.create(
        start_time=start_time,
        end_time=end_time,
        source_incident_id=source_incident_id,
        source=source_system,
        description=description,
        level=level,
        ticket_url=ticket_url,
        metadata=metadata,
    )
    incident.create_first_event()
    if metadata["status"] == "CLOSED":
        incident.set_end(user)


def main(argv):
    force = "--force" in argv
    django.setup()
    if not force and is_initialized():
        print("keeping initialized data")
        return

    purge_db()
    call_command("migrate")
    call_command(
        "initial_setup", password="admin", noc_password="noc", servicedesk_password="servicedesk"
    )
    populate_db(DIR / "incidents")


if __name__ == "__main__":
    main(sys.argv[1:])
