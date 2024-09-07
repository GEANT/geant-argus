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
STATUS_CHECKER_HEALTH_URL = get_str_env(
    "ARGUS_STATUS_CHECKER_HEALTH_URL",
    "https://uat-dashboardv3-monitoring.geant.org:4443/api/health",
)
STATUS_CHECKER_INPROV_URL = get_str_env(
    "ARGUS_STATUS_CHECKER_INPROV_URL", "https://uat-inprov01.geant.org/version"
)
STATUS_CHECKER_UPDATE_INPROV_URL = get_str_env(
    "STATUS_CHECKER_UPDATE_INPROV_URL", "https://uat-inprov01.geant.org/jobs/update"
)
