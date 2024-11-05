from django.conf import settings
import requests

UPDATE_ALARM_URL = "/alarms/{}"
CLOSE_ALARM_URL = "/alarms/{}/close"
CLEAR_ALARM_URL = "/alarms/{}/clear"


def api_url():
    result = getattr(settings, "DASHBOARD_ALARMS_API_URL", None)
    if not result:
        raise ValueError("Please set the ARGUS_DASHBOARD_ALARMS_API_URL environment setting")
    return result


def update_alarm(alarm_id, payload):
    return _succeed_request("PATCH", api_url() + UPDATE_ALARM_URL.format(alarm_id), json=payload)


def close_alarm(alarm_id):
    return _succeed_request("POST", api_url() + CLOSE_ALARM_URL.format(alarm_id))


def clear_alarm(alarm_id, payload):
    return _succeed_request("POST", api_url() + CLEAR_ALARM_URL.format(alarm_id), json=payload)


def _succeed_request(*args, timeout=5, **kwargs) -> bool:
    try:
        response = requests.request(*args, timeout=timeout, **kwargs)
    except requests.Timeout:
        return False
    return response.status_code == 200
