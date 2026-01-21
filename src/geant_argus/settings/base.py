import os

from argus.htmx.appconfig import APP_SETTINGS
from argus.htmx.incident.customization import IncidentTableColumn
from argus.site.settings.base import *  # noqa: F401, F403

update_settings(globals(), APP_SETTINGS)

INSTALLED_APPS = [
    "geant_argus.geant_argus",
    "geant_argus.blacklist",
    "geant_argus.argus_site",
    *INSTALLED_APPS,  # noqa: F405
]
ROOT_URLCONF = "geant_argus.urls"
MIDDLEWARE += [  # noqa: F405
    "geant_argus.geant_argus.metadata.validation.MetadataValidationMiddleware",
    # Unfortunately, due to a bug in CoreAAI, a user's entitlements are cached
    # for an access_token and a refresh_token in the CoreAAI backend, so that rechecking
    # a user's entitlements does not yield updated results even if they have changed. The only
    # thing that works is to force the user to log in again. For this we use the
    # geant_argus.auth.SocialAuthLimitSessionLifetimeMiddleware below. Once the bug has been
    # solved, we can activate (and properly test) the SocialAuthRefreshMiddleware
    #
    # Uncomment the next line to activate SocialAuthRefreshMiddleware
    # "geant_argus.auth.SocialAuthRefreshMiddleware",
    "geant_argus.auth.SocialAuthLimitSessionAgeMiddleware",  # temporary solution
]
if "DATABASES" in globals():
    DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa: F405

MEDIA_PLUGINS = [
    "argus.notificationprofile.media.email.EmailNotification",
]
INDELIBLE_INCIDENTS = False

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    "rest_framework.permissions.IsAuthenticated",
    "geant_argus.auth.IsSuperUserOrSourceSystem",
)


# Remove default template dirs to allow overriding argus.site templates. See also
# geant_argus/argus_site/apps.py
TEMPLATES[0]["DIRS"] = []  # noqa: F405

#  Authentication
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
if not get_bool_env("ARGUS_OIDC_DISABLE", default=False):
    AUTHENTICATION_BACKENDS.append("social_core.backends.open_id_connect.OpenIdConnectAuth")

ARGUS_OIDC_METHOD_NAME = "Geant Federated Login"
ARGUS_OIDC_ENTITLEMENTS_PATTERN = get_str_env("ARGUS_OIDC_ENTITLEMENTS_PATTERN")

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

    # Update the user's authorization
    "geant_argus.auth.update_groups"
)
# fmt: on

SOCIAL_AUTH_LOGIN_ERROR_URL = "/accounts/login"
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

SOCIAL_AUTH_OIDC_OIDC_ENDPOINT = get_str_env("ARGUS_OIDC_URL")
SOCIAL_AUTH_OIDC_KEY = get_str_env("ARGUS_OIDC_CLIENT_ID")
SOCIAL_AUTH_OIDC_SECRET = get_str_env("ARGUS_OIDC_SECRET")

# entitlements are for authorization/groups, offline_access is for refresh_tokens
SOCIAL_AUTH_OIDC_SCOPE = ["entitlements", "offline_access"]

# prompt=consent is a required parameter when requesting the offline_access scope
SOCIAL_AUTH_OIDC_AUTH_EXTRA_ARGUMENTS = {"prompt": "consent"}

# Theming
THEME_DEFAULT = "geant"
STYLESHEET_PATH = "geant.css"
DAISYUI_THEMES = ["light", "dark", "argus", "geant", "geant-test", "geant-uat", "geant-prod"]

# context processors customization
TEMPLATES[0]["OPTIONS"]["context_processors"].extend(
    [
        "geant_argus.geant_argus.context_processors.geant_theme",
        "geant_argus.geant_argus.context_processors.is_readonly",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
    ]
)

AUTH_TOKEN_EXPIRES_AFTER_DAYS = int(os.getenv("ARGUS_AUTH_TOKEN_EXPIRES_AFTER_DAYS", 14))
ARGUS_FILTER_BACKEND = "geant_argus.filter.plugin"
ARGUS_HTMX_FILTER_FUNCTION = ARGUS_FILTER_BACKEND

ARGUS_FRONTEND_DATETIME_FORMAT = "ISO"
TIME_ZONE = "UTC"

INCIDENT_TABLE_COLUMNS = [
    "row_select",
    IncidentTableColumn(
        "level",
        label="Severity",
        cell_template="htmx/incident/cells/_incident_level.html",
        column_classes="min-w-28",
    ),
    IncidentTableColumn(
        "timestamp",
        label="Start Time (UTC)",
        cell_template="htmx/incident/cells/_incident_start_time.html",
    ),
    IncidentTableColumn(
        "status",
        label="Status",
        cell_template="htmx/incident/cells/_incident_status.html",
    ),
    IncidentTableColumn(
        "location",
        label="Location",
        cell_template="htmx/incident/cells/_incident_location_equipment.html",
        context={"field": "location"},
        filter_field="location",
    ),
    IncidentTableColumn(
        "equipment",
        label="Equipment",
        cell_template="htmx/incident/cells/_incident_location_equipment.html",
        context={"field": "equipment"},
        filter_field="equipment",
    ),
    IncidentTableColumn(
        "description",
        label="Description",
        cell_template="htmx/incident/cells/_incident_description.html",
        filter_field="description",
    ),
    IncidentTableColumn(
        "ticket_ref",
        label="TT",
        cell_template="htmx/incident/cells/_incident_ticket_ref.html",
        filter_field="ticket_ref",
    ),
    IncidentTableColumn(
        "ack",
        label="Ack",
        cell_template="htmx/incident/cells/_incident_ack.html",
    ),
    IncidentTableColumn(
        "comment",
        label="Comment",
        cell_template="htmx/incident/cells/_incident_comment.html",
    ),
    IncidentTableColumn(
        "endpoint_count",
        label="#",
        header_template="htmx/incident/cells/_incident_endpoint_count_header.html",
        cell_template="htmx/incident/cells/_incident_endpoint_count.html",
    ),
    IncidentTableColumn(
        "details",
        label="Details",
        cell_template="htmx/incident/cells/_incident_details_button.html",
    ),
]

# Tailwind config template relative to the repository root directory
TAILWIND_CONFIG_TARGET = "tailwindcss/tailwind.config.js"
TAILWIND_CSS_TARGET = "tailwindcss/geant.base.css"


# Status checker widget
STATUS_CHECKER_ENABLED = True
STATUS_CHECKER_HEALTH_URL = os.getenv("ARGUS_STATUS_CHECKER_HEALTH_URL")
STATUS_CHECKER_INPROV_URL = os.getenv("ARGUS_STATUS_CHECKER_INPROV_URL")

# Dashboard Alarms API
DASHBOARD_ALARMS_API_URL = os.getenv("ARGUS_DASHBOARD_ALARMS_API_URL")
DASHBOARD_ALARMS_DISABLE_SYNCHRONIZATION = get_bool_env("DASHBOARD_ALARMS_DISABLE_SYNCHRONIZATION")

# TTS
TICKET_URL_BASE = os.getenv("ARGUS_TICKET_URL_BASE")

# Ivanti Neurons
NEURONS_URL_BASE = os.getenv("ARGUS_NEURONS_URL_BASE")
NEURONS_API_KEY = os.getenv("ARGUS_NEURONS_API_KEY")

# ######### User Preferences options ###########

NEW_INCIDENT_AURAL_ALERTS = ["off", "alert", "beep", "notification"]
NEW_INCIDENT_AURAL_ALERT_DEFAULT = "off"

# Incidents that have not been acked a user's ACK_REMINDER_MINUTES minutes will flash
# on the incident listing
ACK_REMINDER_MINUTES = [0, 5, 10, 15, 30, 60, "never"]
ACK_REMINDER_MINUTES_DEFAULT = 10

DEFAULT_FROM_EMAIL = "noreply@geant.org"

STUCK_ALARM_GRACE_PERIOD_MINUTES = get_int_env("STUCK_ALARM_GRACE_PERIOD_MINUTES", 5)
