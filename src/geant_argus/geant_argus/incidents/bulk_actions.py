from typing import Any, Dict
from argus_htmx.utils import bulk_close_queryset
from django import forms
from django.http import HttpResponseServerError
from geant_argus.geant_argus.dashboard_alarms import close_alarm, clear_alarm
from django.utils import timezone


class ClearAlarmForm(forms.Form):
    timestamp = forms.DateTimeField(required=False)


def bulk_close_incidents(actor, qs, data: Dict[str, Any]):
    incidents = bulk_close_queryset(actor, qs, data)
    for incident in incidents:
        if not close_alarm(incident.source_incident_id):
            raise HttpResponseServerError("Error while closing incident")
        incident.metadata["status"] = "CLOSED"
        incident.metadata["clear_time"] = data["timestamp"].isoformat()
        incident.save()

    return incidents


def bulk_clear_incidents(actor, qs, data: Dict[str, Any]):
    clear_time = (data["timestamp"] or timezone.now()).isoformat()
    incidents = list(qs)
    for incident in incidents:
        if not clear_alarm(incident.source_incident_id, {"clear_time": clear_time}):
            raise HttpResponseServerError("Error while clearing incident")
        incident.metadata["status"] = "CLEAR"
        incident.metadata["clear_time"] = clear_time
        incident.save()

    return incidents
