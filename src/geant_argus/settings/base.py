from argus.site.settings.base import *  # noqa: F401, F403

INSTALLED_APPS = [
    "geant_argus.geant_argus",
    *INSTALLED_APPS,  # noqa: F405
    "django_htmx",
    "argus_htmx",
]
ROOT_URLCONF = "geant_argus.urls"
MIDDLEWARE += ["django_htmx.middleware.HtmxMiddleware"]  # noqa: F405


MEDIA_PLUGINS = [
    "argus.notificationprofile.media.email.EmailNotification",
]
INDELIBLE_INCIDENTS = False
