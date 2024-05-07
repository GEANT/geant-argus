from .base import *  # noqa: F403

SECRET_KEY = get_str_env("SECRET_KEY")  # noqa: F405

DEBUG = True

DISABLE_REDIS = get_bool_env("ARGUS_DISABLE_REDIS")  # noqa: F405
if DISABLE_REDIS:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
