from .base import *

SECRET_KEY = get_str_env("ARGUS_SECRET_KEY")

DEBUG = True

DISABLE_REDIS = get_bool_env("ARGUS_DISABLE_REDIS")
if DISABLE_REDIS:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }