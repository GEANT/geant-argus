import pathlib
from django.apps import AppConfig



class GeantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "geant_argus.geant_argus"

    def tailwind_css_files(self):
        yield from pathlib.Path(__file__).parent.glob("tailwindcss/*.css")

    def ready(self) -> None:
        from argus_htmx.incidents.views import INCIDENT_UPDATE_ACTIONS, DescriptionOptionalForm
        from .incidents.bulk_actions import bulk_close_incidents

        del INCIDENT_UPDATE_ACTIONS['reopen']
        del INCIDENT_UPDATE_ACTIONS['update-ticket']
        INCIDENT_UPDATE_ACTIONS["close"] = (DescriptionOptionalForm, bulk_close_incidents)
