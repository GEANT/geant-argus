from django import forms
from django.core.paginator import Paginator
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from geant_argus.geant_argus.filters.views import render_edit_filter, save_filter_from_request
from geant_argus.blacklist.models import Blacklist
from geant_argus.geant_argus.view_helpers import redirect


class CreateBlacklistForm(ModelForm):
    class Meta:
        model = Blacklist
        fields = ["name", "filter", "level", "message", "enabled", "priority", "review_date"]
        widgets = {"review_date": forms.DateInput(attrs={"type": "date"})}


class EditFilterForBlacklistForm(forms.Form):
    filter = forms.IntegerField(required=False)
    read_only = forms.BooleanField(required=False)


def get_all_blacklists():
    return Blacklist.objects.select_related("filter")


BLACKLISTS_TABLE = {
    "object_id": "blacklist",
    "columns": [
        {"header": "Name", "lookup_key": "name", "width": "w-[10%]"},
        {
            "header": "Severity",
            "width": "w-24",
            "cell_template": "geant/blacklists/_blacklist_level.html",
        },
        {
            "header": "Filter",
            "cell_template": "geant/blacklists/_blacklist_filter.html",
            "width": "w-[20%]",
        },
        {"header": "Message", "lookup_key": "message"},
        {
            "header": "Enabled",
            "cell_template": "geant/blacklists/_blacklist_enabled.html",
            "width": "w-[5%]",
        },
        {"header": "Priority", "lookup_key": "priority", "width": "w-[5%]"},
        {
            "header": "Review Date",
            "cell_template": "geant/blacklists/_blacklist_review_date.html",
            "width": "w-24",
        },
        {"header": "User", "lookup_key": "user"},
        {
            "header": "Actions",
            "width": "w-32",
            "cell_template": "geant/blacklists/_blacklist_actions.html",
        },
    ],
    "add_button": {
        "url": "geant-blacklists:edit-blacklist",
        "text": "Create new blacklist",
    },
}


@require_GET
def list_blacklists(request):
    qs = get_all_blacklists().order_by("name")

    page_num = request.GET.get("page", "1")
    page = Paginator(object_list=qs, per_page=10).get_page(page_num)

    if request.htmx:
        base_template = "components/_table.html"
    else:
        base_template = "geant/blacklists/blacklist_list.html"

    context = {
        "table": BLACKLISTS_TABLE,
        "count": qs.count(),
        "page_title": "Blacklists",
        "page": page,
    }

    return render(request, base_template, context=context)


@require_http_methods(["HEAD", "GET", "POST", "DELETE"])
def edit_blacklist(request, pk=None):
    instance = None if pk is None else get_object_or_404(Blacklist, pk=pk)
    if request.method == "GET":
        context = {"form": CreateBlacklistForm(instance=instance)}
        return render(request, "geant/blacklists/blacklist_edit.html", context=context)
    elif request.method == "POST":
        form = CreateBlacklistForm(request.POST, instance=instance)
        blacklist = form.save(commit=False)
        if not instance:
            blacklist.user = request.user
        blacklist.save()

    elif request.method == "DELETE" and instance is not None:
        instance.delete()
    return redirect(request, target="geant-blacklists:blacklist-list")


@require_GET
def edit_filter(request):
    form = EditFilterForBlacklistForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest("invalid request")
    data = form.cleaned_data

    filter_pk = data.get("filter")
    return render_edit_filter(
        request,
        "geant/blacklists/_blacklist_edit_filter.html",
        pk=filter_pk,
        context={
            "edit_url": reverse(
                "geant-filters:edit-filter", args=(filter_pk,) if filter_pk else ()
            ),
            "read_only": filter_pk and data["read_only"],
        },
    )


@require_POST
def save_filter(request):
    form = EditFilterForBlacklistForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest("invalid request")
    data = form.cleaned_data
    filter_pk = data.get("filter")
    result = save_filter_from_request(request, pk=filter_pk)
    if isinstance(result, HttpResponse):
        # result may be an error response
        return result

    return render_edit_filter(
        request,
        "geant/blacklists/_blacklist_edit_filter.html",
        pk=result.pk,
        context={
            "edit_url": reverse("geant-filters:edit-filter", args=(result.pk,)),
            "read_only": True,
            "form": CreateBlacklistForm({"filter": result.pk}),
        },
    )
