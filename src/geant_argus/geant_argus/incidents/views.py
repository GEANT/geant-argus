import logging

from argus.incident.models import Incident
from django import forms
from django.contrib import messages
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from geant_argus.auth import require_write
from geant_argus.geant_argus.dashboard_alarms import update_alarm
from geant_argus.geant_argus.view_helpers import HtmxHttpRequest, error_response, refresh
from geant_argus.geant_argus.incidents.common import create_ticket_url_and_ticket_link

from .common import EmptyStringAllowedCharField, TicketRefField

logger = logging.getLogger(__name__)


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

    ticket_ref = form.cleaned_data["ticket_ref"]
    if ticket_ref is not None:
        ticket_url, ticket_link, maybe_neurons_error = create_ticket_url_and_ticket_link(
            ticket_ref
        )
        incident.ticket_url = ticket_url
        payload["ticket_link"] = ticket_link

        if maybe_neurons_error:
            messages.error(request, maybe_neurons_error)

    if not update_alarm(incident.source_incident_id, payload=payload):
        messages.error(request, f"Error while updating alarm {incident.source_incident_id}")
        return HttpResponseServerError("Error while updating incident")

    incident.metadata.update(payload)
    incident.save()
    return refresh(request, "htmx:incident-list")
