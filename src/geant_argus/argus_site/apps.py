from django.apps import AppConfig


class ArgusSiteConfig(AppConfig):
    """
    By default, Argus has a TEMPLATES setting (see argus.site.settings.base) that makes it
    impossible to override templates in `argus.site.templates` due to TEMPLATES-> DIRS being
    checked for templates before it looks in apps' templates/ directories. We have fixed this by
    overriding the TEMPLATES settings (see geant_argus.settings.base) to only look for templates in
    app templates/ directories. Now, in order to find the `argus.site` templates we want to add
    `argus.site` as an installed app. However `argus.site` does not have an `apps.py` which may
    result in unforseen behaviour if including the app directly. Instead we provide an AppConfig
    here and point to the `geant.site` package. We then include this app (geant_argus.argus_site)
    in the INSTALLED_APPS setting
    """

    name = "argus.site"
