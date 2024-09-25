from django.conf import settings


def geant_theme(request):
    """Additional context variables specific to Geant"""
    return {
        "theme": request.session.get("theme", getattr(settings, "DEFAULT_THEME", "geant")),
        "path_to_stylesheet": getattr(settings, "DEFAULT_TW_CSS", "geant.css"),
        "logo": {
            "file": "logo_white.png",
            "alt": "geant-argus",
        },
        "incidents_extra_widget": (
            "htmx/status/_status_checker_widget.html"
            if getattr(settings, "STATUS_CHECKER_ENABLED")
            else None
        ),
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
            ],
        },
        "incident_description_glance_table": [
            {
                "name": "Start Time",
                "cell_lookup_key": "start_time",
                "is_meta_item": False,
            },
            {"name": "End Time", "cell_lookup_key": "end_time", "is_meta_item": False},
            {"name": "Status", "cell_lookup_key": "status", "is_meta_item": True},
            {"name": "Severity", "cell_lookup_key": "severity", "is_meta_item": True},
            {"name": "Location", "cell_lookup_key": "location", "is_meta_item": True},
            {"name": "Equipment", "cell_lookup_key": "equipment", "is_meta_item": True},
            {"name": "Full Ticket Ref", "cell_lookup_key": "ticket_ref", "is_meta_item": True},
            {"name": "Description", "cell_lookup_key": "description", "is_meta_item": True},
        ],
    }
