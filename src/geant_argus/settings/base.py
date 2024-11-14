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
# fmt: off
SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. In some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    "social_core.pipeline.social_auth.social_details",

    # Get the social uid from whichever service we"re authing thru. The uid is
    # the unique identifier of the given user in the provider.
    "social_core.pipeline.social_auth.social_uid",

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    "social_core.pipeline.social_auth.auth_allowed",

    # Checks if the current social-account is already associated in the site.
    "social_core.pipeline.social_auth.social_user",

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    "social_core.pipeline.user.get_username",

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    "social_core.pipeline.social_auth.associate_by_email",

    # Create a user account if we haven"t found one yet.
    "social_core.pipeline.user.create_user",

    # Create the record that associates the social account with the user.
    "social_core.pipeline.social_auth.associate_user",

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    "social_core.pipeline.social_auth.load_extra_data",

    # Update the user record with any changed info from the auth service.
    "social_core.pipeline.user.user_details",
)
# fmt: on

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
THEME_DEFAULT = "geant"
STYLESHEET_PATH = "geant.css"
DAISYUI_THEMES = ["light", "dark", "argus", "geant", "geant-test", "geant-uat", "geant-prod"]

# context processors customization
TEMPLATES[0]["OPTIONS"]["context_processors"].extend(
    [
        "geant_argus.geant_argus.context_processors.geant_theme",
        "argus.auth.context_processors.preferences",
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
