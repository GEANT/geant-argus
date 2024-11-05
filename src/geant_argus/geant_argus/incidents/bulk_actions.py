from typing import Any, Dict
from argus_htmx.utils import bulk_close_queryset
from django import forms
from django.http import HttpResponseServerError
from geant_argus.geant_argus.dashboard_alarms import close_alarm


class ClearAlarmForm(forms.Form):
    clear_time = forms.DateTimeField(required=False)


def bulk_close_incidents(actor, qs, data: Dict[str, Any]):
    incidents = bulk_close_queryset(actor, qs, data)
    for incident in incidents:
        if not close_alarm(incident.source_incident_id):
            raise HttpResponseServerError("Error while closing incident")
        incident.metadata["status"] = "CLOSED"
        incident.save()

    return incidents


def bulk_clear_incidents(actor, qs, data: Dict[str, Any]):
    for incident in qs:
        if not close_alarm(incident.source_incident_id):
            raise HttpResponseServerError("Error while closing incident")
        incident.metadata["status"] = "CLOSED"
        incident.save()

    return incidents