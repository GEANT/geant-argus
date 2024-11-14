from argus.incident.models import Incident
from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from geant_argus.geant_argus.dashboard_alarms import update_alarm
from geant_argus.geant_argus.view_helpers import HtmxHttpRequest, refresh

TICKET_URL_BASE = getattr(settings, "TICKET_URL_BASE", "")


@require_POST
def acknowledge_incident(request: HtmxHttpRequest, pk: int):
    incident = get_object_or_404(Incident, id=pk)
    incident.create_ack(request.user, description="Acknowledged using the UI")
    return refresh(request, "htmx:incident-list")


class UpdateIncidentForm(forms.Form):
    comment = forms.CharField(max_length=255, empty_value=None, required=False)
    ticket_ref = forms.CharField(max_length=75, empty_value=None, required=False)


@require_POST
def update_incident(request: HtmxHttpRequest, pk: int):
    form = UpdateIncidentForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest()

    incident = get_object_or_404(Incident, id=pk)
    payload = {k: v for k, v in form.cleaned_data.items() if v is not None}
    if not payload:
        return refresh(request, "htmx:incident-list")

    if not update_alarm(incident.source_incident_id, payload=payload):
        messages.error(request, f"Error while updating alarm {incident.source_incident_id}")
        return HttpResponseServerError("Error while updating incident")

    incident.metadata.update(payload)
    if (ticket_ref := form.cleaned_data["ticket_ref"]) is not None:
        incident.ticket_url = TICKET_URL_BASE + ticket_ref if ticket_ref else ""
    incident.save()

    return refresh(request, "htmx:incident-list")
