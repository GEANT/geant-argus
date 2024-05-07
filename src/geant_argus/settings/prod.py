from argus.site.settings.prod import *  # noqa: F401, F403
from .base import *  # noqa: F401, F403

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEBUG = False
ALLOWED_HOSTS = ["*"]
COOKIE_DOMAIN = None
CORS_ALLOW_ALL_ORIGINS = True

_REDIS_HOSTS = get_str_env("GEANT_REDIS_URLS").split(" ")  # noqa: F405
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": _REDIS_HOSTS,
        },
    },
}

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
