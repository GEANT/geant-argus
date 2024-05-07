from argus.site.settings.prod import *  # noqa: F401, F403
from .base import *  # noqa: F401, F403

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEBUG = False
ALLOWED_HOSTS = ["*"]
COOKIE_DOMAIN = None
CORS_ALLOW_ALL_ORIGINS = True
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
