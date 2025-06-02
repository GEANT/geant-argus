import functools
import itertools
from typing import Any, Dict

from argus.htmx.utils import bulk_close_queryset
from django import forms
from django.conf import settings
from django.http import HttpResponseServerError
from django.utils import timezone
from django.contrib import messages
from geant_argus.auth import has_write_permission
from geant_argus.geant_argus.dashboard_alarms import clear_alarm, close_alarm, update_alarm

from .common import TicketRefField


class TicketRefForm(forms.Form):
    ticket_ref = TicketRefField()


class ClearAlarmForm(forms.Form):
    timestamp = forms.DateTimeField(required=False)


def bulk_action_require_write(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not has_write_permission(request.user):
            messages.error(request, "Insufficient permissions")
            return []
        return func(request, *args, **kwargs)

    return wrapper


@bulk_action_require_write
def bulk_close_incidents(request, qs, data: Dict[str, Any]):
    incidents = bulk_close_queryset(request, qs, data)
    for incident in incidents:
        if not close_alarm(incident.source_incident_id):
            return HttpResponseServerError("Error while closing incident")
        incident.metadata["status"] = "CLOSED"
        incident.metadata["clear_time"] = data["timestamp"].isoformat()
        incident.save()

    return incidents


@bulk_action_require_write
def bulk_clear_incidents(request, qs, data: Dict[str, Any]):
    clear_time = (data["timestamp"] or timezone.now()).isoformat()
    incidents = list(qs)
    for incident in incidents:
        if not clear_alarm(incident.source_incident_id, {"clear_time": clear_time}):
            return HttpResponseServerError("Error while clearing incident")
        clear_incident_in_metadata(incident.metadata, clear_time=clear_time)
        incident.save()

    return incidents


@bulk_action_require_write
def bulk_update_ticket_ref(request, qs, data: Dict[str, Any]):
    ticket_url_base = getattr(settings, "TICKET_URL_BASE", "")
    ticket_ref = data["ticket_ref"]
    payload = {"ticket_ref": ticket_ref}
    incidents = list(qs)
    for incident in incidents:
        if not update_alarm(incident.source_incident_id, payload):
            return HttpResponseServerError("Error while updating ticket_ref")

        incident.metadata.update(payload)
        incident.ticket_url = ticket_url_base + ticket_ref if ticket_ref else ""
        incident.save()
    return incidents


def clear_incident_in_metadata(metadata: dict, clear_time: str):
    metadata["status"] = "CLEAR"
    metadata["clear_time"] = clear_time

    # Iteration masturbation. We want to iterate over every endpoint and also get it's endpoint
    # type. Could do nested for loops, but this is more "functional" and has less indentation.
    endpoints = itertools.chain.from_iterable(
        zip(itertools.repeat(ept_type), endpoints)
        for ept_type, endpoints in metadata["endpoints"].items()
    )
    events = itertools.chain.from_iterable(
        zip(itertools.repeat(ept_type), endpoint["events"]) for ept_type, endpoint in endpoints
    )

    down_events = (evt for evt in events if not evt[1]["is_up"])
    for endpoint_type, event in down_events:
        event["is_up"] = True
        event["clear_time"] = clear_time
        properties = event["properties"]
        if endpoint_type == "bgp":
            properties["establish_time"] = clear_time
            properties["status"] = "established"
        elif endpoint_type == "link":
            properties["oper_up_time"] = clear_time
            properties["oper_status"] = "up"
        elif endpoint_type in ("coriant", "infinera", "fiberlink"):
            properties["status"] = "Clear"
