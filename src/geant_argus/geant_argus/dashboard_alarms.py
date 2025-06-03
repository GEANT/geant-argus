from django.conf import settings
from http import HTTPStatus
import requests

UPDATE_ALARM_URL = "/alarms/{}"
ACK_ALARM_URL = "/alarms/{}/ack"
CLOSE_ALARM_URL = "/alarms/{}/close"
CLEAR_ALARM_URL = "/alarms/{}/clear"

ERROR_MESSAGES = {404: "Alarm not found", 400: "Bad request, alarm may be pending"}


def api_url():
    result = getattr(settings, "DASHBOARD_ALARMS_API_URL", None)
    disable_synchronization = getattr(settings, "DASBHOARD_ALARMS_DISABLE_SYNCHRONIZATION", False)
    if not result and not disable_synchronization:
        raise ValueError("Please set the ARGUS_DASHBOARD_ALARMS_API_URL environment setting")
    return result


def update_alarm(alarm_id, payload):
    return _succeed_request("PATCH", api_url() + UPDATE_ALARM_URL.format(alarm_id), json=payload)


def close_alarm(alarm_id):
    return _succeed_request("POST", api_url() + CLOSE_ALARM_URL.format(alarm_id))


def clear_alarm(alarm_id, payload):
    return _succeed_request("POST", api_url() + CLEAR_ALARM_URL.format(alarm_id), json=payload)


def _succeed_request(*args, timeout=5, **kwargs) -> str | None:
    disable_synchronization = getattr(settings, "DASBHOARD_ALARMS_DISABLE_SYNCHRONIZATION", False)
    if disable_synchronization:
        return None
    try:
        response = requests.request(*args, timeout=timeout, **kwargs)
    except requests.Timeout:
        return "Request timed out while updating alarm"
    if response.status_code != 200:
        error_description = ERROR_MESSAGES.get(
            response.status_code, HTTPStatus(response.status_code).description
        )
        return f"{error_description} (HTTP {response.status_code})"
