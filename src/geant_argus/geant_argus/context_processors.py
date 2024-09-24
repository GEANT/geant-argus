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
                    "classes": "w-2/12",
                },
                {
                    "name": "Remote Peer",
                    "cell_template": "htmx/incident_details/bgp_remote_peer.html",
                    "is_endpoint_column": True,
                    "classes": "w-2/12",
                },
                {
                    "name": "Alarm ID",
                    "cell_template": "htmx/incident_details/event_id.html",
                    "classes": "w-1/12",
                },
                {
                    "name": "Status",
                    "cell_template": "htmx/incident_details/event_status.html",
                    "classes": "w-1/12",
                },
                {
                    "name": "Init Time (UTC)",
                    "cell_template": "htmx/incident_details/event_init_time.html",
                    "classes": "w-2/12",
                },
                {
                    "name": "Clear Time (UTC)",
                    "cell_template": "htmx/incident_details/event_clear_time.html",
                    "classes": "w-2/12",
                },
                {
                    "name": "Properties",
                    "cell_template": "htmx/incident_details/event_properties.html",
                    "classes": "w-2/12",
                },
            ],
            "link": [
                {
                    "name": "Hostname",
                    "cell_template": "htmx/incident_details/hostname.html",
                    "is_endpoint_column": True,
                    "classes": "w-2/12",
                },
                {
                    "name": "Interface",
                    "cell_template": "htmx/incident_details/link_interface.html",
                    "is_endpoint_column": True,
                    "classes": "w-2/12",
                },
                {
                    "name": "Alarm ID",
                    "cell_template": "htmx/incident_details/event_id.html",
                    "classes": "w-1/12",
                },
                {
                    "name": "Status",
                    "cell_template": "htmx/incident_details/event_status.html",
                    "classes": "w-1/12",
                },
                {
                    "name": "Init Time (UTC)",
                    "cell_template": "htmx/incident_details/event_init_time.html",
                    "classes": "w-2/12",
                },
                {
                    "name": "Clear Time (UTC)",
                    "cell_template": "htmx/incident_details/event_clear_time.html",
                    "classes": "w-2/12",
                },
                {
                    "name": "Properties",
                    "cell_template": "htmx/incident_details/event_properties.html",
                    "classes": "w-1/12",
                },
            ],
            "coriant": [
                {
                    "name": "NE Name",
                    "cell_template": "htmx/incident_details/optical_ne_name.html",
                    "is_endpoint_column": True,
                    "classes": "w-2/12",
                },
                {
                    "name": "Port",
                    "cell_template": "htmx/incident_details/optical_port.html",
                    "is_endpoint_column": True,
                    "classes": "w-2/12",
                },
                {
                    "name": "Alarm ID",
                    "cell_template": "htmx/incident_details/event_id.html",
                    "classes": "w-1/12",
                },
                {
                    "name": "Status",
                    "cell_template": "htmx/incident_details/event_status.html",
                    "classes": "w-1/12",
                },
                {
                    "name": "Init Time (UTC)",
                    "cell_template": "htmx/incident_details/event_init_time.html",
                    "classes": "w-2/12",
                },
                {
                    "name": "Clear Time (UTC)",
                    "cell_template": "htmx/incident_details/event_clear_time.html",
                    "classes": "w-2/12",
                },
                {
                    "name": "Properties",
                    "cell_template": "htmx/incident_details/event_properties.html",
                    "classes": "w-1/12",
                },
            ],
            "infinera": [
                {
                    "name": "NE Name",
                    "cell_template": "htmx/incident_details/optical_ne_name.html",
                    "is_endpoint_column": True,
                    "classes": "w-2/12",
                },
                {
                    "name": "Port",
                    "cell_template": "htmx/incident_details/optical_port.html",
                    "is_endpoint_column": True,
                    "classes": "w-2/12",
                },
                {
                    "name": "Alarm ID",
                    "cell_template": "htmx/incident_details/event_id.html",
                    "classes": "w-1/12",
                },
                {
                    "name": "Status",
                    "cell_template": "htmx/incident_details/event_status.html",
                    "classes": "w-1/12",
                },
                {
                    "name": "Init Time (UTC)",
                    "cell_template": "htmx/incident_details/event_init_time.html",
                    "classes": "w-2/12",
                },
                {
                    "name": "Clear Time (UTC)",
                    "cell_template": "htmx/incident_details/event_clear_time.html",
                    "classes": "w-2/12",
                },
                {
                    "name": "Properties",
                    "cell_template": "htmx/incident_details/event_properties.html",
                    "classes": "w-1/12",
                },
            ],
        },
    }
