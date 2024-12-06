import pathlib
from django.apps import AppConfig


class GeantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "geant_argus.geant_argus"

    def tailwind_css_files(self):
        yield from pathlib.Path(__file__).parent.glob("tailwindcss/*.css")

    def ready(self) -> None:
        from argus.htmx.incidents.views import (
            INCIDENT_UPDATE_ACTIONS,
            DescriptionOptionalForm,
            AckForm,
        )
        from .incidents.bulk_actions import (
            bulk_close_incidents,
            bulk_clear_incidents,
            bulk_ack_incidents,
            ClearAlarmForm,
        )

        del INCIDENT_UPDATE_ACTIONS["reopen"]
        del INCIDENT_UPDATE_ACTIONS["update-ticket"]
        INCIDENT_UPDATE_ACTIONS["ack"] = (AckForm, bulk_ack_incidents)
        INCIDENT_UPDATE_ACTIONS["close"] = (DescriptionOptionalForm, bulk_close_incidents)
        INCIDENT_UPDATE_ACTIONS["clear"] = (ClearAlarmForm, bulk_clear_incidents)
