from argus.incident.models import Incident
from django import forms
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST, require_GET
from django_htmx.middleware import HtmxDetails
from django.db.models import Q

ACK_GROUPS = ("noc", "servicedesk")


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


class AckForm(forms.Form):
    group = forms.ChoiceField(choices=list(zip(ACK_GROUPS, ACK_GROUPS)), required=False)
    comment = forms.CharField(max_length=255, required=False)
    source = forms.ChoiceField(
        choices=[("checkbox", "checkbox"), ("comment", "comment")], required=True
    )


def can_ack(user, group=None):
    where = Q(name__in=ACK_GROUPS) if group is None else Q(name=group)
    return user.groups.filter(where).exists()


@require_POST
def acknowledge_incident(request: HtmxHttpRequest, pk: int):
    form = AckForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Bad request")

    group = form.cleaned_data.get("group")
    comment = form.cleaned_data.get("comment")
    source = form.cleaned_data["source"]
    incident = get_object_or_404(Incident, id=pk)

    status = 401
    ack = None
    if can_ack(request.user):
        ack = incident.create_ack(request.user, description=comment or "")
        status = 200

    if source == "checkbox":
        template = "htmx/incidents/_incident_group_ack.html"
    else:
        template = "htmx/incidents/_incident_comment_ack.html"

    context = {"column": {"context": group}, "incident": incident, "ack": ack}
    return render(request, template, context=context, status=status)


@require_GET
def begin_comment(request: HtmxHttpRequest, pk: int):
    return render(
        request,
        "htmx/incidents/_incident_comment_ack.html",
        context={"is_editing": True, "pk": pk},
    )
