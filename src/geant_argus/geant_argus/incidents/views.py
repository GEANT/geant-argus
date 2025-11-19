import requests
import logging

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

logger = logging.getLogger(__name__)

TICKET_URL_BASE = getattr(settings, "TICKET_URL_BASE", "")
NEURONS_URL_BASE = getattr(settings, "NEURONS_URL_BASE", "")
NEURONS_API_KEY = getattr(settings, "NEURONS_API_KEY", "")
NEURONS_TICKET_URL = (
    f"{NEURONS_URL_BASE}/login.aspx?Scope=ObjectWorkspace&CommandId=Search&ObjectType="
)


class UpdateIncidentForm(forms.Form):
    comment = EmptyStringAllowedCharField(max_length=255, empty_value=None, required=False)
    ticket_ref = TicketRefField()


def lookup_neurons_ticket_url(ticket_number):
    if NEURONS_URL_BASE is None:
        return None
    search_url_incident = (
        NEURONS_URL_BASE
        + f"/api/odata/businessobject/Incidents?$filter=IncidentNumber eq {ticket_number}"
    )
    search_url_maintenance = (
        NEURONS_URL_BASE
        + f"/api/odata/businessobject/Changes?$filter=ChangeNumber eq {ticket_number}"
    )
    headers = {"Authorization": f"rest_api_key={NEURONS_API_KEY}"}

    response_maintenance = requests.get(search_url_maintenance, headers=headers)
    if response_maintenance.status_code == 200:
        maintenance_data = response_maintenance.json()["value"]
        rec_id = maintenance_data[0]["RecId"]
        return (
            NEURONS_TICKET_URL
            + f"Change%23&CommandData=RecId%2C%3D%2C0%2C{rec_id}%2Cstring%2CAND%2C%7C"
        )
    elif response_maintenance.status_code != 204:  # API returns 204 if no ticket is found
        logger.error(
            f"Neurons maintenance ticket query API error: {response_maintenance.status_code}"
        )

    response_incident = requests.get(search_url_incident, headers=headers)
    if response_incident.status_code == 200:
        incident_data = response_incident.json()["value"]
        rec_id = incident_data[0]["RecId"]
        return f"{NEURONS_TICKET_URL}Incident%23&CommandData=RecId%2C%3D%2C0%2C{rec_id}"
    elif response_incident.status_code != 204:  # API returns 204 if no ticket is found
        logger.error(f"Neurons incident ticket query API error: {response_incident.status_code}")


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
        new_ticket_url = lookup_neurons_ticket_url(ticket_ref)
        if new_ticket_url is None:
            new_ticket_url = TICKET_URL_BASE + ticket_ref if ticket_ref else ""
        payload["ticket_link"] = new_ticket_url
        incident.ticket_url = new_ticket_url

    if not update_alarm(incident.source_incident_id, payload=payload):
        messages.error(request, f"Error while updating alarm {incident.source_incident_id}")
        return HttpResponseServerError("Error while updating incident")

    incident.metadata.update(payload)
    incident.save()
    return refresh(request, "htmx:incident-list")
