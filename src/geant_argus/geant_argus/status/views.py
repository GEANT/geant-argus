from datetime import datetime
import time
from django.conf import settings
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpRequest
from django.shortcuts import render
from argus.util.datetime_utils import make_aware
import requests

from geant_argus.auth import require_write

CORRELATOR_REL_TIME = [
    [300, ">5 min"],
    [120, ">2 min"],
    [60, ">1 min"],
    [30, "<1 min"],
    [0, "<30s"],
]


@require_GET
def service_status(request: HttpRequest):
    return render(
        request, "htmx/status/_status_checker_widget_content.html", context=get_service_info()
    )


@require_POST
@require_write()
def update_inventory(request: HttpRequest):
    send_update_inprov()
    return render(
        request, "htmx/status/_status_checker_widget_content.html", context=get_service_info()
    )


def get_service_info():
    health = get_services_health()
    inprov_status = get_inprov_status()
    return {
        "services": {
            "Correlator": single_service_status(health, "correlator"),
            "Forwarder": single_service_status(health, "collector"),
            "Classifier": single_service_status(health, "classifier"),
            "Inventory Provider": single_service_status(health, "inventory"),
        },
        "last_correlated": get_trap_last_correlated(
            health.get("correlator", {}).get("timestamp", 0)
        ),
        "inventory": get_inventory_update_status(inprov_status.get("latch")),
        "inventory_ui_url": settings.STATUS_CHECKER_INPROV_URL + "/static/update.html",
    }


def get_services_health():
    return _get_or_empty(settings.STATUS_CHECKER_HEALTH_URL)


def get_inprov_status():
    return _get_or_empty(settings.STATUS_CHECKER_INPROV_URL + "/version")


def send_update_inprov():
    return _get_or_empty(settings.STATUS_CHECKER_INPROV_URL + "/jobs/update")


def _get_or_empty(*args, timeout=10, **kwargs):
    try:
        response = requests.get(*args, timeout=timeout, **kwargs)
    except requests.Timeout:
        return {}
    if response.status_code >= 400:
        return {}
    return response.json()


def single_service_status(health, service):
    if not (info := health.get(service)):
        return {"color": "slate-300", "message": "No info"}
    status_to_color = {"healthy": "success"}
    return {
        "color": status_to_color.get(info["status"], info["status"]),
        "message": info["message"],
    }


def get_trap_last_correlated(timestamp: int):
    if not timestamp:
        return "?"
    diff = time.time() - timestamp
    for breakpoint, msg in CORRELATOR_REL_TIME:
        if diff > breakpoint:
            return msg
    return CORRELATOR_REL_TIME[-1][1]


def get_inventory_update_status(latch):
    return {
        "last_update": (
            make_aware(datetime.fromtimestamp(int(timestamp)))
            if (timestamp := latch.get("timestamp"))
            else "N/A"
        ),
        "pending": latch.get("pending"),
    }
