import datetime
import json

from argus.auth.models import User
from argus.incident.models import Incident
from django import template
from django.template.defaultfilters import stringfilter
from django.utils import timezone
from ..incidents.severity import IncidentSeverity

register = template.Library()


def _level_to_severity(value):
    min_level = min(IncidentSeverity)
    max_level = max(IncidentSeverity)
    level = max(min_level, min(max_level, value))
    return IncidentSeverity(level)


@register.filter(name="to_severity")
def level_to_severity(value):
    """Removes all values of arg from the given string"""
    return _level_to_severity(value).name


@register.filter(name="levelbadge")
def level_to_badge(incident: Incident):
    severity = _level_to_severity(incident.level)
    match severity:
        case IncidentSeverity.CRITICAL:
            color = "incident-critical"
        case IncidentSeverity.MAJOR:
            color = "incident-major"
        case IncidentSeverity.MINOR:
            color = "incident-minor"
        case IncidentSeverity.WARNING:
            color = "incident-warning"
        case _:
            return "badge-outline-ghost"

    return f'bg-{color}{"/50" if not incident.open else ""} border-{color}'


def _incident_status(incident: Incident):
    if incident.open:
        return upperfirst(incident.metadata.get("status", "Active"))
    return "Closed"


@register.filter(name="incidentstatus")
def incident_status_text(incident: Incident):
    return _incident_status(incident)


@register.filter(name="statusbadge")
def incident_status_badge(incident: Incident):
    status = _incident_status(incident)
    match status:
        case "Active":
            return "badge-primary"
        case "Clear":
            return "bg-incident-clear border-incident-clear"
        case "Closed":
            return "badge-outline-ghost"


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


ACK_GROUPS = ("noc", "sd")
MUST_ACK_TIMEDELTA = datetime.timedelta(hours=2, minutes=10)


@register.filter
def is_acked(incident, group: str | None = None) -> bool:
    """Backport of filter with the same name in argus-htmx-frontend"""
    if not group:
        group = ACK_GROUPS
    if isinstance(group, str):
        group = [group]

    return any((getattr(incident, f"{g}_ack", None) for g in group))


@register.filter
def must_ack(incident: Incident, group: str | None = None):
    is_ack = is_acked(incident, group)
    print(incident.start_time)
    return not is_ack and timezone.now() > incident.start_time + MUST_ACK_TIMEDELTA
