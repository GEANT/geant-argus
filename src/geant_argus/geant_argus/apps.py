import pathlib
from django.apps import AppConfig


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
            bulk_ack_incidents,
            ClearAlarmForm,
        )

        views.INCIDENT_UPDATE_ACTIONS = {
            "ack": (views.AckForm, bulk_ack_incidents),
            "close": (views.DescriptionOptionalForm, bulk_close_incidents),
            "clear": (ClearAlarmForm, bulk_clear_incidents),
        }
