import pathlib
from django.apps import AppConfig


class GeantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "geant_argus.geant_argus"

    # def tailwind_css_files(self):
    #     yield pathlib.Path(__file__).parent / "tailwindcss/11-anytthing.css"
