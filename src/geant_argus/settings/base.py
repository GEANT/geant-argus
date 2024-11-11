import os

from argus.site.settings.base import *  # noqa: F401, F403
from argus_htmx.incidents.customization import IncidentTableColumn
from argus_htmx.settings import *  # noqa: F403

INSTALLED_APPS = [
    "geant_argus.geant_argus",
    "geant_argus.argus_site",
    *INSTALLED_APPS,  # noqa: F405
    "django_htmx",
    "argus_htmx",
    "widget_tweaks",
]
ROOT_URLCONF = "geant_argus.urls"
MIDDLEWARE += [  # noqa: F405
    "django_htmx.middleware.HtmxMiddleware",
    "argus_htmx.middleware.LoginRequiredMiddleware",
    "argus_htmx.middleware.HtmxMessageMiddleware",
    "geant_argus.geant_argus.metadata.validation.MetadataValidationMiddleware",
]
if "DATABASES" in globals():
    DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa: F405

MEDIA_PLUGINS = [
    "argus.notificationprofile.media.email.EmailNotification",
]
INDELIBLE_INCIDENTS = False

# Remove default template dirs to allow overriding argus.site templates. See also
# geant_argus/argus_site/apps.py
TEMPLATES[0]["DIRS"] = []  # noqa: F405

#  Authentication
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.open_id_connect.OpenIdConnectAuth",
]
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    # Here we deviate from the default pipeline to support whitelisting users by email addresss
    "social_core.pipeline.social_auth.associate_by_email",
    "geant_argus.auth.require_existing_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

SOCIAL_AUTH_LOGIN_ERROR_URL = "/accounts/login"
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

ARGUS_OIDC_METHOD_NAME = "Geant Federated Login"
SOCIAL_AUTH_OIDC_OIDC_ENDPOINT = get_str_env("ARGUS_OIDC_URL")
SOCIAL_AUTH_OIDC_KEY = get_str_env("ARGUS_OIDC_CLIENT_ID")
SOCIAL_AUTH_OIDC_SECRET = get_str_env("ARGUS_OIDC_SECRET")

PUBLIC_URLS = [
    "/accounts/login/",
    "/api/",
    "/oidc/",
]

# Theming
DEFAULT_THEME = "geant"
DEFAULT_TW_CSS = "geant.css"
DAISYUI_THEMES = ["light", "dark", "argus", "geant", "geant-test", "geant-uat", "geant-prod"]

# context processors customization
TEMPLATES[0]["OPTIONS"]["context_processors"].extend(
    [
        "geant_argus.geant_argus.context_processors.geant_theme",
        "argus_htmx.context_processors.datetime_format_via_session",
    ]
)

AUTH_TOKEN_EXPIRES_AFTER_DAYS = int(os.getenv("ARGUS_AUTH_TOKEN_EXPIRES_AFTER_DAYS", 14))
ARGUS_FILTER_BACKEND = "geant_argus.geant_argus.filters.plugin"
ARGUS_HTMX_FILTER_FUNCTION = ARGUS_FILTER_BACKEND

ARGUS_FRONTEND_DATETIME_FORMAT = "ISO"
TIME_ZONE = "UTC"

INCIDENT_TABLE_COLUMNS = [
    "row_select",
    IncidentTableColumn(
        "timestamp",
        label="Start Time (UTC)",
        cell_template="htmx/incidents/_incident_start_time.html",
    ),
    IncidentTableColumn(
        "status",
        label="Status",
        cell_template="htmx/incidents/_incident_status.html",
    ),
    IncidentTableColumn(
        "level",
        label="Severity",
        cell_template="htmx/incidents/_incident_level.html",
    ),
    IncidentTableColumn(
        "location",
        label="Location",
        cell_template="htmx/incidents/_incident_location_equipment.html",
        context={"field": "location"},
    ),
    IncidentTableColumn(
        "equipment",
        label="Equipment",
        cell_template="htmx/incidents/_incident_location_equipment.html",
        context={"field": "equipment"},
    ),
    IncidentTableColumn(
        "description",
        label="Description",
        cell_template="htmx/incidents/_incident_description.html",
    ),
    IncidentTableColumn(
        "ticket_ref",
        label="TT",
        cell_template="htmx/incidents/_incident_ticket_ref.html",
    ),
    IncidentTableColumn(
        "ack",
        label="Ack",
        cell_template="htmx/incidents/_incident_ack.html",
    ),
    IncidentTableColumn(
        "comment",
        label="Comment",
        cell_template="htmx/incidents/_incident_comment.html",
    ),
    IncidentTableColumn(
        "endpoint_count",
        label="#",
        header_template="htmx/incidents/_incident_endpoint_count_header.html",
        cell_template="htmx/incidents/_incident_endpoint_count.html",
    ),
    IncidentTableColumn(
        "details",
        label="Details",
        cell_template="htmx/incidents/_incident_details_button.html",
    ),
]

# Tailwind config template relative to the repository root directory
TAILWIND_CONFIG_TARGET = "tailwindcss/tailwind.config.js"
TAILWIND_CSS_TARGET = "tailwindcss/geant.base.css"


# Status checker widget
STATUS_CHECKER_ENABLED = True
STATUS_CHECKER_HEALTH_URL = os.getenv("ARGUS_STATUS_CHECKER_HEALTH_URL")
STATUS_CHECKER_INPROV_URL = os.getenv("ARGUS_STATUS_CHECKER_INPROV_URL")

# Incidents that have not been acked within MUST_ACK_WITHIN_MINUTES minutes will flash
# on the incident listing
MUST_ACK_WITHIN_MINUTES = get_int_env("ARGUS_MUST_ACK_WITHIN_MINUTES", default=None)

# Dashboard Alarms API
DASHBOARD_ALARMS_API_URL = os.getenv("ARGUS_DASHBOARD_ALARMS_API_URL")

# TTS
TICKET_URL_BASE = os.getenv("ARGUS_TICKET_URL_BASE")
