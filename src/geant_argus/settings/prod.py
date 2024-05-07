from argus.site.settings.prod import *  # noqa: F401, F403
from .base import *  # noqa: F401, F403

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEBUG = False
ALLOWED_HOSTS = ["*"]
COOKIE_DOMAIN = None
CORS_ALLOW_ALL_ORIGINS = True
