import logging
import requests

from django import forms
from django.core import validators
from django.conf import settings
from django.utils.regex_helper import _lazy_re_compile

TICKET_URL_BASE = getattr(settings, "TICKET_URL_BASE", "")
NEURONS_URL_BASE = getattr(settings, "NEURONS_URL_BASE", "")
NEURONS_API_KEY = getattr(settings, "NEURONS_API_KEY", "")
NEURONS_TICKET_URL = (
    f"{NEURONS_URL_BASE}/login.aspx?Scope=ObjectWorkspace&CommandId=Search&ObjectType="
)

logger = logging.getLogger(__name__)


class EmptyStringAllowedCharField(forms.CharField):
    empty_values = (None,)  # empty string '' should not be considered an empty value


class TicketRefField(forms.CharField):
    default_validators = (
        validators.RegexValidator(
            _lazy_re_compile(r"^\d{0,16}\Z"),
            message="Enter a valid ticket number.",
            code="invalid",
        ),
    )
    empty_values = (None,)  # empty string '' should not be considered an empty value


def lookup_neurons_ticket_url(ticket_number) -> tuple[str | None, str | None]:
    """
    Tries to find a matching ticket in neurons using the provided ticket number.
    Checks both incident and maintenance tickets.

    :param ticket_number: ticket number
    :type ticket_number: str
    :return: A tuple of a ticket URL if found and any API errors the user should know of.
    :rtype: tuple[str | None, str | None]
    """
    if NEURONS_URL_BASE is None:
        return None, None
    search_url_incident = (
        NEURONS_URL_BASE
        + f"/api/odata/businessobject/Incidents?$filter=IncidentNumber eq {ticket_number}"
    )
    search_url_maintenance = (
        NEURONS_URL_BASE
        + f"/api/odata/businessobject/Changes?$filter=ChangeNumber eq {ticket_number}"
    )
    headers = {"Authorization": f"rest_api_key={NEURONS_API_KEY}"}

    # Check maintenance tickets
    response_maintenance = requests.get(search_url_maintenance, headers=headers)
    if response_maintenance.status_code == 200:
        maintenance_data = response_maintenance.json()["value"]
        rec_id = maintenance_data[0]["RecId"]
        return (
            NEURONS_TICKET_URL
            + f"Change%23&CommandData=RecId%2C%3D%2C0%2C{rec_id}%2Cstring%2CAND%2C%7C"
        ), None
    elif response_maintenance.status_code != 204:  # API returns 204 if no ticket is found
        error_message = f"Neurons maintenance query API error: {response_maintenance.status_code}"
        logger.error(error_message)
        return None, error_message

    # Check incident tickets
    response_incident = requests.get(search_url_incident, headers=headers)
    if response_incident.status_code == 200:
        incident_data = response_incident.json()["value"]
        rec_id = incident_data[0]["RecId"]
        return (f"{NEURONS_TICKET_URL}Incident%23&CommandData=RecId%2C%3D%2C0%2C{rec_id}"), None
    elif response_incident.status_code != 204:  # API returns 204 if no ticket is found
        error_message = f"Neurons incident query API error: {response_incident.status_code}"
        logger.error(error_message)
        return None, error_message

    return None, None


def create_ticket_url_and_ticket_link(ticket_number: str) -> tuple[str, str, str | None]:
    """
    Given a ticket number return the ticket URL.
    If a ticket number is found in Neurons a URL for that will be provided otherwise a link
    for Otobo will be created no matter what the ticket number is.
    If we generated a non-otobo link we also want that stored in AlarmsDB in the ticket_link field

    :param ticket_number: ticket number
    :type ticket_number: str
    :return: A tuple of the ticket URL to be displayed in Argus, the ticket link to be
        stored in AlarmsDB, and finally any errors/warnings that should be propagated to the user.
    :rtype: tuple[str, str, str | None]
    """
    if not ticket_number:
        return "", "", None
    neurons_url, maybe_neurons_error = lookup_neurons_ticket_url(ticket_number)
    if neurons_url is None:
        otobo_ticket_url = TICKET_URL_BASE + ticket_number
        return otobo_ticket_url, "", maybe_neurons_error
    else:
        return neurons_url, neurons_url, maybe_neurons_error
