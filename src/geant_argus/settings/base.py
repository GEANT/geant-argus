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
        label="Timestamp",
        cell_template="htmx/incidents/_incident_start_time.html",
    ),
    IncidentTableColumn(
        "endpoint_count",
        label="Flaps",
        cell_template="htmx/incidents/_incident_endpoint_count.html",
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
        "alarm_id",
        label="Alarm ID",
        cell_template="htmx/incidents/_incident_source_incident_id.html",
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
        "noc_ack",
        label="NOC Ack",
        cell_template="htmx/incidents/_incident_group_ack.html",
        context={"group": "noc"},
    ),
    IncidentTableColumn(
        "sd_ack",
        label="SD Ack",
        cell_template="htmx/incidents/_incident_group_ack.html",
        context={"group": "servicedesk"},
    ),
    IncidentTableColumn(
        "details",
        label="Details",
        cell_template="htmx/incidents/_incident_details_button.html",
    ),
]

# Tailwind config template relative to the repository root directory
TAILWIND_CONFIG_TEMPLATE = "tailwindcss/tailwind.config.template.js"
TAILWIND_CONFIG_TARGET = "tailwindcss/tailwind.config.js"


# Status checker widget
STATUS_CHECKER_ENABLED = True
STATUS_CHECKER_HEALTH_URL = os.getenv("ARGUS_STATUS_CHECKER_HEALTH_URL")
STATUS_CHECKER_INPROV_URL = os.getenv("ARGUS_STATUS_CHECKER_INPROV_URL")
STATUS_CHECKER_UPDATE_INPROV_URL = os.getenv("ARGUS_STATUS_CHECKER_UPDATE_INPROV_URL")

# Incidents that have not been acked within MUST_ACK_WITHIN_MINUTES minutes will flash
# on the incident listing
MUST_ACK_WITHIN_MINUTES = get_int_env("ARGUS_MUST_ACK_WITHIN_MINUTES", default=None)
