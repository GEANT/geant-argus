import json

from argus.auth.models import User
from argus.incident.models import Incident
from django import template
from django.template.defaultfilters import stringfilter

from ..incidents.severity import IncidentSeverity

register = template.Library()


@register.filter(name="to_severity")
def level_to_severity(value):
    """Removes all values of arg from the given string"""
    min_level = min(IncidentSeverity)
    max_level = max(IncidentSeverity)
    level = max(min_level, min(max_level, value))
    return IncidentSeverity(level).name


@register.filter
def json_pp(value):
    """pretty formats as json if possible"""
    try:
        return json.dumps(value, indent=2)
    except TypeError:
        return value


@register.filter
@stringfilter
def upperfirst(value: str):
    if not value:
        return ""
    return value[0].upper() + value[1:].lower()


@register.filter
def has_group(user: User, group):
    return user.groups.filter(name=group).exists()


@register.filter
def is_acked_by(incident, group: str) -> bool:
    """Backport of filter with the same name in argus-htmx-frontend"""
    # TODO: remove once argus-htmx-frontend v0.5 is released
    return incident.is_acked_by(group)


@register.filter
def row_classes(incident: Incident):
    status = incident.metadata.get("status", "").upper()
    if status == "CLEAR":
        return "bg-incident-clear"
    match IncidentSeverity(incident.level):
        case IncidentSeverity.CRITICAL:
            color = "bg-incident-critical"
        case IncidentSeverity.MAJOR:
            color = "bg-incident-major"
        case IncidentSeverity.MINOR:
            color = "bg-incident-minor"
        case IncidentSeverity.WARNING:
            color = "bg-incident-warning"
        case _:
            color = ""
    if color and status == "CLOSED":
        color = f"{color}/50"
    return color
