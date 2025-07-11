from django.conf import settings
from geant_argus.auth import has_write_permission

INCIDENT_DETAILS_COMMON_COLUMNS = [
    {"name": "Alarm ID", "cell_template": "htmx/incident_details/event_id.html"},
    {"name": "Status", "cell_template": "htmx/incident_details/event_status.html"},
    {
        "name": "Init Time (UTC)",
        "cell_template": "htmx/incident_details/event_init_time.html",
    },
    {
        "name": "Clear Time (UTC)",
        "cell_template": "htmx/incident_details/event_clear_time.html",
    },
    {
        "name": "Properties",
        "cell_template": "htmx/incident_details/event_properties.html",
    },
]


def geant_theme(request):
    """Additional context variables specific to Geant"""
    return {
        "logo": {
            "file": "logo_white.png",
            "alt": "geant-argus",
        },
        "incidents_extra_widget": (
            "htmx/status/_status_checker_widget.html"
            if getattr(settings, "STATUS_CHECKER_ENABLED")
            else None
        ),
        "short_alarms_ui_url": getattr(settings, "SHORT_LIVED_ALARMS_UI_URL", None),
        "incident_details_tables": {
            "bgp": [
                {
                    "name": "Hostname",
                    "cell_template": "htmx/incident_details/hostname.html",
                    "is_endpoint_column": True,
                },
                {
                    "name": "Remote Peer",
                    "cell_template": "htmx/incident_details/bgp_remote_peer.html",
                    "is_endpoint_column": True,
                },
                *INCIDENT_DETAILS_COMMON_COLUMNS,
            ],
            "link": [
                {
                    "name": "Hostname",
                    "cell_template": "htmx/incident_details/hostname.html",
                    "is_endpoint_column": True,
                },
                {
                    "name": "Interface",
                    "cell_template": "htmx/incident_details/link_interface.html",
                    "is_endpoint_column": True,
                },
                *INCIDENT_DETAILS_COMMON_COLUMNS,
            ],
            "coriant": [
                {
                    "name": "NE Name",
                    "cell_template": "htmx/incident_details/optical_ne_name.html",
                    "is_endpoint_column": True,
                },
                {
                    "name": "Port",
                    "cell_template": "htmx/incident_details/optical_port.html",
                    "is_endpoint_column": True,
                },
                *INCIDENT_DETAILS_COMMON_COLUMNS,
            ],
            "infinera": [
                {
                    "name": "NE Name",
                    "cell_template": "htmx/incident_details/optical_ne_name.html",
                    "is_endpoint_column": True,
                },
                {
                    "name": "Port",
                    "cell_template": "htmx/incident_details/optical_port.html",
                    "is_endpoint_column": True,
                },
                *INCIDENT_DETAILS_COMMON_COLUMNS,
            ],
            "fiberlink": [
                {
                    "name": "NE A",
                    "cell_template": "htmx/incident_details/fiberlink_ne_a.html",
                    "is_endpoint_column": True,
                },
                {
                    "name": "NE B",
                    "cell_template": "htmx/incident_details/fiberlink_ne_b.html",
                    "is_endpoint_column": True,
                },
                *INCIDENT_DETAILS_COMMON_COLUMNS,
            ],
        },
        "incident_description_glance_table": [
            {"name": "Description", "cell_lookup_key": "description"},
            {
                "name": "Initial Start Time (UTC)",
                "cell_lookup_key": "metadata.earliest_source_init_time",
                "cell_template": "htmx/incident/cells/_date_cell.html",
                "info_text": "When the alarm very first started.",
            },
            {
                "name": "Recent Alarm Outage Time (UTC)",
                "cell_lookup_key": "start_time",
                "cell_template": "htmx/incident/cells/_date_cell.html",
                "info_text": "The start time of the most recent alarm.",
            },
            {
                "name": "Clear Time (UTC)",
                "cell_lookup_key": "metadata.clear_time",
                "cell_template": "htmx/incident/cells/_date_cell.html",
            },
            {"name": "Alarm ID", "cell_lookup_key": "source_incident_id"},
            {"name": "Status", "cell_lookup_key": "metadata.status"},
            {"name": "Severity", "cell_lookup_key": "metadata.severity"},
            {"name": "Location", "cell_lookup_key": "metadata.location"},
            {"name": "Equipment", "cell_lookup_key": "metadata.equipment"},
            {"name": "Full Ticket Ref", "cell_lookup_key": "metadata.ticket_ref"},
            {"name": "Comment", "cell_lookup_key": "metadata.comment"},
            {"name": "Acked by", "cell_lookup_key": "ack_user"},
            {
                "name": "Short lived?",
                "cell_lookup_key": "metadata.short_lived",
                "cell_template": "htmx/incident/cells/_boolean_cell.html",
            },
        ],
    }


def is_readonly(request):
    return {"readonly": not has_write_permission(request.user)}
