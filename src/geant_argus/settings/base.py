from argus.site.settings.base import *

SECRET_KEY = get_str_env("ARGUS_SECRET_KEY")

INSTALLED_APPS = [
    "geant_argus.geant_argus",
    *INSTALLED_APPS,
    "django_htmx",
    "argus_htmx",
]
ROOT_URLCONF = "geant_argus.urls"
MIDDLEWARE += ["django_htmx.middleware.HtmxMiddleware"]


MEDIA_PLUGINS = [
    "argus.notificationprofile.media.email.EmailNotification",
]
