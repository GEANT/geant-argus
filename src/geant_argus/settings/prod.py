from .base import *  # noqa: F403
from argus.site.settings.prod import *  # noqa: F403

SECRET_KEY = get_str_env("ARGUS_SECRET_KEY")  # noqa: F405
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEBUG = False
ALLOWED_HOSTS = ["*"]
