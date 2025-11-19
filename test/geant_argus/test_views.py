from geant_argus.geant_argus.incidents.views import lookup_neurons_ticket_url
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
    result = lookup_neurons_ticket_url(11111)
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
    result = lookup_neurons_ticket_url(11111)
    parsed = urlparse(result)
    assert parsed.scheme is not None
    assert parsed.netloc is not None
    assert result == (
        "https://geant-ism-amc-uat.ivanticloud.com/login.aspx"
        "?Scope=ObjectWorkspace&CommandId=Search&ObjectType=Change%23"
        "&CommandData=RecId%2C%3D%2C0%2C9999999%2Cstring%2CAND%2C%7C"
    )
