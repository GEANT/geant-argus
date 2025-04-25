from argus.incident.models import Incident
from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from geant_argus.auth import require_write
from geant_argus.geant_argus.dashboard_alarms import update_alarm
from geant_argus.geant_argus.view_helpers import HtmxHttpRequest, error_response, refresh

from .common import EmptyStringAllowedCharField, TicketRefField

TICKET_URL_BASE = getattr(settings, "TICKET_URL_BASE", "")


class UpdateIncidentForm(forms.Form):
    comment = EmptyStringAllowedCharField(max_length=255, empty_value=None, required=False)
    ticket_ref = TicketRefField()


@require_POST
@require_write("htmx:incident-list")
def update_incident(request: HtmxHttpRequest, pk: int):
    form = UpdateIncidentForm(request.POST)
    if not form.is_valid():
        messages.error(request, form.errors)
        return error_response(request, "htmx:incident-list")

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
