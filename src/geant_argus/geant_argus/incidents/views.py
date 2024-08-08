from argus.incident.models import Incident
from django import forms
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django_htmx.middleware import HtmxDetails


def prefetch_incident_daughters():
    return Incident.objects.select_related("source").prefetch_related(
        "incident_tag_relations",
        "incident_tag_relations__tag",
        "events",
        "events__ack",
        "events__actor",
        "events__actor__groups",
    )


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


class AckForm(forms.Form):
    group = forms.ChoiceField(
        choices=(("noc", "noc"), ("servicedesk", "servicedesk")), required=True
    )


@require_POST
def acknowledge_incident(request: HtmxHttpRequest, pk: int):
    form = AckForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest("invalid group")

    group = form.cleaned_data["group"]
    incident = get_object_or_404(Incident, id=pk)

    is_group_member = request.user.groups.filter(name=group).exists()
    if not is_group_member:
        status = 401
    else:
        incident.create_ack(request.user, description="Acknowledged using the UI")
        status = 200
    context = {"column": {"context": group}, "incident": incident, "is_ack": True}
    return render(
        request, "htmx/incidents/_incident_group_ack.html", context=context, status=status
    )
