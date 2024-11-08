from argus.site.settings.backend import *  # noqa: F401, F403
from .base import *  # noqa: F401, F403

STORAGES["staticfiles"][
    "BACKEND"
] = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

DEBUG = False
ALLOWED_HOSTS = [".geant.org"]
if FRONTEND_URL:
    CSRF_TRUSTED_ORIGINS = [FRONTEND_URL]
COOKIE_DOMAIN = None

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
DEFAULT_TW_CSS = "geant.min.css"
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 15  # 15MB
