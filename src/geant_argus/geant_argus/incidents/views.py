from argus.incident.models import Incident
from django import forms
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_htmx.middleware import HtmxDetails
from django_htmx.http import HttpResponseClientRefresh


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


class AckForm(forms.Form):
    group = forms.ChoiceField(
        choices=(("noc", "noc"), ("servicedesk", "servicedesk")), required=True
    )


def refresh(request: HtmxHttpRequest, target):
    redirect_to = reverse(target)
    if request.htmx:
        return HttpResponseClientRefresh()
    return redirect(redirect_to)


@require_POST
def acknowledge_incident(request: HtmxHttpRequest, pk: int):
    form = AckForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest("invalid group")

    group = form.cleaned_data["group"]
    incident = get_object_or_404(Incident, id=pk)

    is_group_member = request.user.groups.filter(name=group).exists()
    if is_group_member:
        incident.create_ack(request.user, description="Acknowledged using the UI")

    return refresh("htmx:incident-list")


@require_POST
def update_comment(request: HtmxHttpRequest, pk: int):
    comment = request.POST.get("comment")
    if comment is not None:
        incident = get_object_or_404(Incident, id=pk)
        incident.metadata["comment"] = comment
        incident.metadata["dirty"] = True
        incident.save()
    return refresh(request, "htmx:incident-list")
