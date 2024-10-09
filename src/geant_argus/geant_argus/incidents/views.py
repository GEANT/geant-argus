from argus.incident.models import Incident
from django import forms
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django_htmx.middleware import HtmxDetails

ACK_GROUPS = ("noc", "servicedesk")


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


class AckForm(forms.Form):
    group = forms.ChoiceField(choices=list(zip(ACK_GROUPS, ACK_GROUPS)), required=False)


def can_ack(user, group=None):
    where = Q(name__in=ACK_GROUPS) if group is None else Q(name=group)
    return user.groups.filter(where).exists()


@require_POST
def acknowledge_incident(request: HtmxHttpRequest, pk: int):
    form = AckForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Bad request")

    group = form.cleaned_data.get("group")
    incident = get_object_or_404(Incident, id=pk)

    is_group_member = request.user.groups.filter(name=group).exists()
    if is_group_member:
        incident.create_ack(request.user, description="Acknowledged using the UI")

    redirect_to = reverse("htmx:incident-list")
    if request.htmx:
        redirect_to = request.htmx.current_url_abs_path or redirect_to
        return HttpResponse(headers={"HX-Redirect": redirect_to})
    return redirect(redirect_to)


@require_GET
def begin_comment(request: HtmxHttpRequest, pk: int):
    return render(
        request,
        "htmx/incidents/_incident_comment_ack.html",
        context={"is_editing": True, "pk": pk},
    )
