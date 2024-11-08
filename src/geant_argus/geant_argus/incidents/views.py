from argus.incident.models import Incident
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from geant_argus.geant_argus.dashboard_alarms import update_alarm
from geant_argus.geant_argus.view_helpers import HtmxHttpRequest, refresh


@require_POST
def acknowledge_incident(request: HtmxHttpRequest, pk: int):
    incident = get_object_or_404(Incident, id=pk)
    incident.create_ack(request.user, description="Acknowledged using the UI")
    return refresh(request, "htmx:incident-list")


@require_POST
def update_comment(request: HtmxHttpRequest, pk: int):
    comment = request.POST.get("comment")
    if comment is not None:
        incident = get_object_or_404(Incident, id=pk)
        if not update_alarm(incident.source_incident_id, {"comment": comment}):
            return HttpResponseServerError("Error while updating incident")
        incident.metadata["comment"] = comment
        incident.save()
    return refresh(request, "htmx:incident-list")
