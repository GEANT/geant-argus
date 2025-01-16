import datetime
import json

from argus.incident.models import Incident
from django import template
from django.conf import settings
from django.http import HttpRequest
from django.template.defaultfilters import stringfilter
from django.utils import timezone
from argus.auth.utils import get_preference
from ..incidents.severity import IncidentSeverity
from .template_utils import dateparse, get_item

register = template.Library()


def _level_to_severity(value):
    min_level = min(IncidentSeverity)
    max_level = max(IncidentSeverity)
    level = max(min_level, min(max_level, value))
    return IncidentSeverity(level)


@register.filter(name="to_severity")
def level_to_severity(value):
    return _level_to_severity(value).name


@register.filter(name="incidentlevelbadge")
def incident_level_to_badge(incident: Incident):
    return level_to_badge(incident.level, incident.open)


@register.filter(name="levelbadge")
def level_to_badge(level: int, is_open=True):
    severity = _level_to_severity(level)
    match severity:
        case IncidentSeverity.CRITICAL:
            classes = ["incident-critical"]
        case IncidentSeverity.MAJOR:
            classes = ["incident-major"]

        case IncidentSeverity.MINOR:
            classes = ["incident-minor"]
        case _:
            classes = ["incident-default"]
    if not is_open:
        classes.append("incident-closed")
    return " ".join(classes)


@register.filter(name="incidentblacklistcolor")
def incident_blacklist_color(incident: Incident):
    severity = incident.metadata.get("blacklist", {}).get("original_severity", "").lower()
    if severity in {"critical", "major", "minor"}:
        return severity
    return "default"


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
            return "incident-clear"
        case "Closed":
            return "incident-default"


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
def is_acked(incident, group: str) -> bool:
    return bool(getattr(incident, f"{group}_ack", None))


MUST_ACK_TIMEDELTA = datetime.timedelta(minutes=10)


@register.filter
def must_ack(incident: Incident):
    must_ack_timedelta = None
    if (must_ack_within_minutes := getattr(settings, "MUST_ACK_WITHIN_MINUTES", None)) is not None:
        must_ack_timedelta = datetime.timedelta(minutes=must_ack_within_minutes)
    return (
        not getattr(incident, "ack", True)
        and can_ack(incident)
        and must_ack_timedelta is not None
        and timezone.now() > incident.start_time + must_ack_timedelta
    )


@register.filter
def can_ack(incident: Incident):
    return (
        incident.metadata.get("phase", "").upper() != "PENDING"
        and incident.metadata.get("status", "").upper() != "CLOSED"
    )


@register.filter
def blacklist_symbol(incident: Incident):
    match incident.metadata:
        case {"blacklist": {"original_severity": str(severity)}} if severity in IncidentSeverity:
            if IncidentSeverity[severity] > incident.level:
                return "▲"
            if IncidentSeverity[severity] == incident.level:
                return "="
            if IncidentSeverity[severity] < incident.level:
                return "▼"
        case _:
            return "?"


@register.filter
def duration(incident: Incident):
    end_time = (
        dateparse(clear_time)
        if (clear_time := incident.metadata.get("clear_time"))
        else datetime.datetime.now()
    ).astimezone(datetime.timezone.utc)
    return end_time - incident.start_time


@register.filter
def get_quick_glance_item(obj, item):
    key = item["cell_lookup_key"]
    value = get_item(obj, key.split("."))

    if isinstance(value, list):
        return " - ".join(str(v) for v in value)

    return value


@register.filter
def get_aural_alert(request: HttpRequest):
    if get_preference(request, "geant_argus", "aural_alert") == "off":
        return None
    if request.session.get("geant.new_pending_incidents"):
        return "alert"
    return None
