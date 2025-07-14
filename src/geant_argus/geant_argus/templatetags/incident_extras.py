import datetime
import functools
import json

from argus.auth.utils import get_preference
from argus.incident.models import Incident
from django import template
from django.conf import settings
from django.core.signals import setting_changed
from django.http import HttpRequest
from django.template.defaultfilters import stringfilter
from django.utils import timezone

from ..incidents.severity import IncidentSeverity
from .template_utils import dateparse, get_item

register = template.Library()


@functools.cache
def stuck_alarms_grace_period():
    return datetime.timedelta(minutes=settings.STUCK_ALARM_GRACE_PERIOD_MINUTES)


setting_changed.connect(lambda **_: stuck_alarms_grace_period.cache_clear())


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
    return level_to_badge(
        incident.level, incident.metadata.get("status", "active").lower() != "closed"
    )


@register.filter(name="levelbadge")
def level_to_badge(level: int, is_open=True):
    severity = _level_to_severity(level)
    match severity:
        case IncidentSeverity.CRITICAL:
            classes = ["incident-critical"]
        case IncidentSeverity.HIGH:
            classes = ["incident-high"]
        case IncidentSeverity.MEDIUM:
            classes = ["incident-medium"]

        case IncidentSeverity.LOW:
            classes = ["incident-low"]
        case _:
            classes = ["incident-default"]
    if is_open:
        classes.append("border-base-content")
    if not is_open:
        classes.extend(["incident-closed", "border-base-content/50"])
    return " ".join(classes)


@register.filter(name="incidentstatus")
def incident_status(incident: Incident):
    clearing_since = dateparse(incident.metadata.get("clearing_since"))
    limit = datetime.datetime.now() - stuck_alarms_grace_period()
    status = upperfirst(incident.metadata.get("status", "Active"))
    phase = incident.metadata.get("phase", "FINALIZED").upper()
    if (
        phase == "FINALIZED"
        and status == "Active"
        and clearing_since is not None
        and clearing_since < limit
    ):
        status = "Stuck"
    return status


@register.filter(name="statusbadge")
def incident_status_badge(incident: Incident):
    status = incident_status(incident)
    match status:
        case "Active":
            return "badge-primary"
        case "Clear":
            return "incident-clear"
        case "Stuck":
            return "incident-major"
        case "Closed":
            return "incident-default"


@register.filter(name="statustitletext")
def incident_status_title_text(incident: Incident):
    status = incident_status(incident)
    match status:
        case "Active":
            return "This alarm is actively down"
        case "Clear":
            return "This alarm has fully cleared"
        case "Stuck":
            return (
                "This alarm has sub alarms which are still down,"
                " please review the details button and pass over to 2nd line OUTSIDE RED HOURS"
            )
        case "Closed":
            return "This alarm has fully cleared and has been acknowledged and closed"


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
def must_ack(incident: Incident, ack_reminder):
    must_ack_timedelta = None
    try:
        ack_reminder = int(ack_reminder)
    except (TypeError, ValueError):
        pass
    if isinstance(ack_reminder, int):
        must_ack_timedelta = datetime.timedelta(minutes=ack_reminder)
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
    # TODO: this should fix itself when you rename the alarm severities in AlarmsDB
    #  (argus api.py line 88)
    match incident.metadata:
        case {"hidden": True}:
            return "H"
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
    if not request.session.get("geant.new_pending_incidents"):
        return None

    alert = get_preference(request, "geant_argus", "aural_alert")

    if alert not in settings.NEW_INCIDENT_AURAL_ALERTS:
        alert = settings.NEW_INCIDENT_AURAL_ALERT_DEFAULT
    if alert == "on":
        alert = "alert"

    if alert == "off":
        return None

    return alert
