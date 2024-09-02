from django.conf import settings


def geant_theme(request):
    """Set the argus theme in the render context"""
    return {
        "theme": request.session.get("theme", getattr(settings, "DEFAULT_THEME", "geant")),
        "path_to_stylesheet": getattr(settings, "DEFAULT_TW_CSS", "geant.css"),
        "logo": {
            "file": "logo_white.png",
            "alt": "geant-argus",
        },
        "incidents_extra_widget": "htmx/status/_services_status_widget.html",
    }
