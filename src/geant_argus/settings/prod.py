from .base import *  # noqa: F403

SECRET_KEY = get_str_env("ARGUS_SECRET_KEY")  # noqa: F405

DEBUG = False
ALLOWED_HOSTS = ["*"]
