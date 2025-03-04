import django_filters as df
from django import forms
from django.core.paginator import Paginator
from django.forms import ModelForm, modelform_factory
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from geant_argus.blacklist.models import Blacklist
from geant_argus.geant_argus.filters.views import render_edit_filter, save_filter_from_request
from geant_argus.geant_argus.view_helpers import HtmxHttpRequest, redirect


class CreateBlacklistForm(ModelForm):
    class Meta:
        model = Blacklist
        fields = ["name", "filter", "level", "message", "enabled", "priority", "review_date"]
        widgets = {"review_date": forms.DateInput(attrs={"type": "date"})}


class EditFilterForBlacklistForm(forms.Form):
    filter = forms.IntegerField(required=False)
    read_only = forms.BooleanField(required=False)


class BlacklistFilter(df.FilterSet):
    name = df.CharFilter("name", lookup_expr="icontains")
    message = df.CharFilter("message", lookup_expr="icontains")
    filtertext = df.CharFilter(
        field_name="filtertext",
        method="filter_filtertext",
        label="Filter text",
    )
    enabled = df.BooleanFilter("enabled")
    review_date = df.DateFilter("review_date")
    order_by = df.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("name", "name"),
            ("enabled", "enabled"),
            ("review_date", "review_date"),
            ("level", "severity"),
        ),
    )

    class Meta:
        model = Blacklist
        fields = ["name", "message", "review_date", "filtertext"]

    def filter_filtertext(self, queryset, name, value):
        if not value:
            return queryset
        objects_ids = [obj.pk for obj in queryset.all() if value.lower() in obj.filtertext.lower()]
        if objects_ids:
            queryset = queryset.filter(pk__in=objects_ids)
        else:
            queryset = queryset.none()
        return queryset


def get_all_blacklists():
    return Blacklist.objects.select_related("filter")


def blacklist_table(form: forms.Form):
    return {
        "object_id": "blacklist",
        "list": {"url": "geant-blacklists:list-blacklists"},
        "filter_form": form,
        "ordering_field": "order_by",
        "columns": [
            {
                "header": "Name",
                "lookup_key": "name",
                "width": "w-[10%]",
                "filter_field": "name",
                "filter_by": True,
                "order_by": True,
            },
            {
                "header": "Severity",
                "width": "w-24",
                "cell_template": "geant/blacklists/_blacklist_level.html",
                "filter_field": "severity",
                "order_by": True,
            },
            {
                "header": "Filter",
                "cell_template": "geant/blacklists/_blacklist_filter.html",
                "width": "w-[20%]",
                "filter_field": "filtertext",
                "filter_by": True,
            },
            {
                "header": "Message",
                "lookup_key": "message",
                "filter_field": "message",
                "filter_by": True,
            },
            {
                "header": "Enabled",
                "cell_template": "geant/blacklists/_blacklist_enabled.html",
                "width": "w-[5%]",
                "filter_field": "enabled",
                "order_by": True,
            },
            {
                "header": "Priority",
                "lookup_key": "priority",
                "width": "w-[5%]",
                "header_template": "geant/blacklists/_blacklist_priority_header.html",
                "filter_field": "priority",
                "order_by": True,
            },
            {
                "header": "Review Date",
                "cell_template": "geant/blacklists/_blacklist_review_date.html",
                "width": "w-24",
                "filter_field": "review_date",
                "order_by": True,
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
    f = BlacklistFilter(request.GET, queryset=get_all_blacklists().order_by("name"))
    if not f.is_valid():
        return HttpResponseBadRequest("Bad request")

    page_num = request.GET.get("page", "1")
    page = Paginator(object_list=f.qs, per_page=10).get_page(page_num)

    if request.htmx:
        base_template = "components/_table.html"
    else:
        base_template = "geant/blacklists/blacklist_list.html"

    context = {
        "table": blacklist_table(f.form),
        "count": f.qs.count(),
        "page_title": "Blacklists",
        "page": page,
        "filter": f,
    }

    return render(request, base_template, context=context)


@require_http_methods(["HEAD", "GET", "POST", "DELETE"])
def edit_blacklist(request: HtmxHttpRequest, pk=None):
    instance = None if pk is None else get_object_or_404(Blacklist, pk=pk)
    if request.method == "GET":
        context = {"form": CreateBlacklistForm(instance=instance)}
        return render(request, "geant/blacklists/blacklist_edit.html", context=context)
    elif request.method == "POST":
        Form = CreateBlacklistForm
        if only_fields := request.POST.getlist("_only"):
            # simple validation to limit updating fields
            assert set(only_fields).issubset(set(Form.Meta.fields))
            Form = modelform_factory(Blacklist, form=Form, fields=only_fields)
        form = Form(request.POST, instance=instance)
        blacklist = form.save(commit=False)
        if not instance:
            blacklist.user = request.user
        blacklist.save()

    elif request.method == "DELETE" and instance is not None:
        instance.delete()
    return redirect(request, target="geant-blacklists:list-blacklists")


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
            # Upon save we need to update the blacklist filter <select> element because the filter
            # name may be changed. We do this through an htmx oob swap of that element (see also
            # `templates/geant/blacklists/_blacklist_edit_filter.html`). We use a BlacklistForm
            # to render the <select> exactly the same as the original <select>
            "blacklist_form": CreateBlacklistForm({"filter": result.pk}),
        },
    )
