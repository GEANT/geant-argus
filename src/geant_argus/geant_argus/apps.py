import os
import pathlib
from django.apps import AppConfig
from django.conf import settings
from django.utils.autoreload import autoreload_started

from geant_argus.settings.config import load_config


class GeantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "geant_argus.geant_argus"

    def tailwind_css_files(self):
        yield from pathlib.Path(__file__).parent.glob("tailwindcss/*.css")

    def ready(self) -> None:
        from argus.htmx.incident import views
        from .incidents.bulk_actions import (
            bulk_close_incidents,
            bulk_clear_incidents,
            bulk_update_ticket_ref,
            ClearAlarmForm,
            TicketRefForm,
        )

        views.INCIDENT_UPDATE_ACTIONS = {
            "ack": views.INCIDENT_UPDATE_ACTIONS["ack"],
            "close": (views.DescriptionOptionalForm, bulk_close_incidents),
            "clear": (ClearAlarmForm, bulk_clear_incidents),
            "ticket_ref": (TicketRefForm, bulk_update_ticket_ref),
        }

        # We read the config file here so that we can override settings that are set
        # in the settings file
        config_filename = os.getenv("CONFIG_FILENAME")
        if config_filename:
            load_config(config_filename, settings)
            # hook up the config.json to django's runserver autoreloader
            autoreload_started.connect(
                lambda sender, **_: sender.extra_files.add(pathlib.Path(config_filename))
            )
