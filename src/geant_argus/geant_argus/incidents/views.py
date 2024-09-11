from argus.incident.models import Incident
from django import forms
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_htmx.middleware import HtmxDetails


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
    if is_group_member:
        incident.create_ack(request.user, description="Acknowledged using the UI")

    redirect_to = reverse("htmx:incident-list")
    if request.htmx:
        # HX-Current-URL may contain query params that we want to keep. use incident-list
        # as a fallback option
        redirect_to = request.headers.get("HX-Current-URL", redirect_to)
        return HttpResponse(headers={"HX-Redirect": redirect_to})
    return redirect(redirect_to)
