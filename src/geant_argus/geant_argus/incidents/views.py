from argus.incident.models import Incident
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

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
        incident.metadata["comment"] = comment
        incident.metadata["dirty"] = True
        incident.save()
    return refresh(request, "htmx:incident-list")
