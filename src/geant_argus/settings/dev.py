from .base import *  # noqa: F403

DEBUG = True

DISABLE_REDIS = get_bool_env("ARGUS_DISABLE_REDIS")  # noqa: F405
if DISABLE_REDIS:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }

SECRET_KEY = get_str_env("SECRET_KEY", "secret-secret!")  # noqa: F405
STATIC_URL = get_str_env("STATIC_URL", "/static/")  # noqa: F405
STATIC_ROOT = get_str_env("STATIC_ROOT", "staticfiles/")  # noqa: F405
