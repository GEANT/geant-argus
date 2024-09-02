from datetime import datetime
import time
from django.views.decorators.http import require_GET
from django.http import HttpRequest
from django.shortcuts import render
from argus.util.datetime_utils import make_aware

CORRELATOR_REL_TIME = [
    [300, ">5 min"],
    [120, ">2 min"],
    [60, ">1 min"],
    [30, "<1 min"],
    [0, "<30s"],
]

HEALTH = {
    "classifier": {"message": "OK", "status": "healthy", "timestamp": 1725266813},
    "collector": {"message": "no FORWARDER processes found", "status": "error", "timestamp": -1},
    "correlator": {
        "message": "OK (leader is uat-noc-alarms-vm01.geant.org)",
        "status": "healthy",
        "timestamp": 1725266813,
    },
    "inventory": {
        "message": "update in progress (last updated 8 minutes ago)",
        "status": "warning",
        "timestamp": 1725266286,
    },
}

INPROV_VERSION = {
    "api": "0.1",
    "latch": {
        "current": 0,
        "failure": False,
        "next": 3,
        "pending": True,
        "this": 0,
        "timestamp": 1725266286.3155851,
        "update-started": 1725266797.034249,
    },
    "module": "0.129",
}


def single_service_status(health, service):
    info = health[service]
    status_to_color = {"healthy": "success"}
    return {
        "color": status_to_color.get(info["status"], info["status"]),
        "message": info["message"],
    }


def get_trap_last_correlated(timestamp: int):
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
        "pending": latch["pending"],
    }


@require_GET
def service_status(request: HttpRequest):
    context = {
        "services": {
            "Correlator": single_service_status(HEALTH, "correlator"),
            "Forwarder": single_service_status(HEALTH, "collector"),
            "Classifier": single_service_status(HEALTH, "classifier"),
            "Inventory Provider": single_service_status(HEALTH, "inventory"),
        },
        "last_correlated": get_trap_last_correlated(HEALTH["correlator"]["timestamp"]),
        "inventory": get_inventory_update_status(INPROV_VERSION["latch"]),
    }
    return render(request, "htmx/status/_services_status_widget_content.html", context=context)
