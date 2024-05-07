from .base import *  # noqa: F401, F403
from argus.site.settings.prod import *  # noqa: F401, F403

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEBUG = False
ALLOWED_HOSTS = ["*"]
COOKIE_DOMAIN = None
