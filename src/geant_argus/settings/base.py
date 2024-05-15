from argus.site.settings.base import *  # noqa: F401, F403

INSTALLED_APPS = [
    "geant_argus.geant_argus",
    "geant_argus.argus_site",
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
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": get_bool_env("TEMPLATE_DEBUG", False),  # noqa: F405
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    }
]
