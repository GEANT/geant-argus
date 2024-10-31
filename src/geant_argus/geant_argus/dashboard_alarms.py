from django.conf import settings
import requests

UPDATE_ALARM_URL = "/alarms/{}"
CLOSE_ALARM_URL = "/alarms/{}/close"
CLEAR_ALARM_URL = "/alarms/{}/clear"


def update_alarm(alarm_id, payload):
    API_URL = getattr(settings, "DASHBOARD_ALARMS_API_URL", None)
    if not API_URL:
        raise ValueError("Please set the ARGUS_DASHBOARD_ALARMS_API_URL environment setting")
    return _succeed_request("PATCH", API_URL + UPDATE_ALARM_URL.format(alarm_id), json=payload)


def _succeed_request(*args, timeout=5, **kwargs) -> bool:
    try:
        response = requests.request(*args, timeout=timeout, **kwargs)
    except requests.Timeout:
        return False
    return response.status_code == 200
