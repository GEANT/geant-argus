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
]
ROOT_URLCONF = "geant_argus.urls"
MIDDLEWARE += [  # noqa: F405
    "django_htmx.middleware.HtmxMiddleware",
    "geant_argus.geant_argus.metadata.validation.MetadataValidationMiddleware",
]
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
# context processor for theming
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "geant_argus.geant_argus.context_processors.geant_theme"
)

AUTH_TOKEN_EXPIRES_AFTER_DAYS = int(os.getenv("ARGUS_AUTH_TOKEN_EXPIRES_AFTER_DAYS", 14))
ARGUS_FILTER_BACKEND = "geant_argus.geant_argus.filters.plugin"
ARGUS_HTMX_FILTER_FUNCTION = ARGUS_FILTER_BACKEND

INCIDENT_TABLE_COLUMNS = [
    "row_select",
    "start_time",
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
        "description",
        label="Description",
        cell_template="htmx/incidents/_incident_description.html",
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
