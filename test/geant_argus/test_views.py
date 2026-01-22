from geant_argus.geant_argus.incidents.common import (
    lookup_neurons_ticket_url,
    create_ticket_url_and_ticket_link,
)
from test import settings
import responses
from urllib.parse import urlparse


@responses.activate
def test_lookup_neurons_ticket_url_incident():
    responses.get(
        settings.NEURONS_URL_BASE + "/api/odata/businessobject/Incidents",
        json={"value": [{"RecId": "9999999"}]},
    )
    responses.get(settings.NEURONS_URL_BASE + "/api/odata/businessobject/Changes", status=204)
    result, _ = lookup_neurons_ticket_url("11111")
    parsed = urlparse(result)
    assert parsed.scheme is not None
    assert parsed.netloc is not None
    assert result == (
        "https://geant-ism-amc-uat.ivanticloud.com/login.aspx"
        "?Scope=ObjectWorkspace&CommandId=Search&ObjectType=Incident%23"
        "&CommandData=RecId%2C%3D%2C0%2C9999999"
    )


@responses.activate
def test_lookup_neurons_ticket_url_maintenance():
    responses.get(settings.NEURONS_URL_BASE + "/api/odata/businessobject/Incidents", status=204)
    responses.get(
        settings.NEURONS_URL_BASE + "/api/odata/businessobject/Changes",
        json={"value": [{"RecId": "9999999"}]},
    )
    result, _ = lookup_neurons_ticket_url("11111")
    parsed = urlparse(result)
    assert parsed.scheme is not None
    assert parsed.netloc is not None
    assert result == (
        "https://geant-ism-amc-uat.ivanticloud.com/login.aspx"
        "?Scope=ObjectWorkspace&CommandId=Search&ObjectType=Change%23"
        "&CommandData=RecId%2C%3D%2C0%2C9999999%2Cstring%2CAND%2C%7C"
    )


@responses.activate
def test_create_ticket_url_and_ticket_link_neurons():
    responses.get(
        settings.NEURONS_URL_BASE + "/api/odata/businessobject/Incidents",
        json={"value": [{"RecId": "9999999"}]},
    )
    responses.get(
        settings.NEURONS_URL_BASE + "/api/odata/businessobject/Changes",
        status=204,
    )
    ticket_url, ticket_link, maybe_neurons_error = create_ticket_url_and_ticket_link("11111")
    expected_url = (
        "https://geant-ism-amc-uat.ivanticloud.com/login.aspx"
        "?Scope=ObjectWorkspace&CommandId=Search&ObjectType=Incident%23"
        "&CommandData=RecId%2C%3D%2C0%2C9999999"
    )
    assert ticket_url == expected_url
    assert ticket_link == expected_url
    assert maybe_neurons_error is None


@responses.activate
def test_create_ticket_url_and_ticket_link_otobo():
    responses.get(
        settings.NEURONS_URL_BASE + "/api/odata/businessobject/Incidents",
        status=204,
    )
    responses.get(
        settings.NEURONS_URL_BASE + "/api/odata/businessobject/Changes",
        status=204,
    )
    ticket_url, ticket_link, maybe_neurons_error = create_ticket_url_and_ticket_link("11111")
    expected_url = (
        "https://tts.geant.net/otrs/index.pl?Action\\=AgentTicketZoom\\;TicketNumber\\=11111"
    )
    assert ticket_url == expected_url
    assert ticket_link == ""
    assert maybe_neurons_error is None
