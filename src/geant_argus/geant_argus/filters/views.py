import re
from typing import Optional

from argus.filter.filters import Filter
from argus.incident.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .filters import FILTER_MODEL


def get_all_filters():
    return Filter.objects.select_related("user")


def list_filter_context(request):
    # Load incidents
    qs = get_all_filters().order_by("name")

    # Standard Django pagination
    page_num = request.GET.get("page", "1")
    page = Paginator(object_list=qs, per_page=10).get_page(page_num)

    return {
        "column_count": 3,
        "count": qs.count(),
        "page_title": "Filters",
        "page": page,
    }


def default_edit_context():
    return {"name": "", "model": FILTER_MODEL}


@require_GET
def list_filters(request):
    # The htmx magic - use a different, minimal base template for htmx
    # requests, allowing us to skip rendering the unchanging parts of the
    # template.
    if request.htmx:
        base_template = "geant/filters/_filter_table.html"
    else:
        base_template = "geant/filters/filter_list.html"

    context = list_filter_context(request)
    return render(request, base_template, context=context)


@require_http_methods(["HEAD", "GET", "POST", "DELETE"])
def edit_filter(request, pk: Optional[int] = None, create=False):
    if request.method == "GET":
        if pk:
            filter = get_object_or_404(Filter, pk=pk)
            filter_dict = filter.filter
        else:
            filter = None
            filter_dict = FILTER_MODEL.default_rule()
        context = {
            **list_filter_context(request),
            **default_edit_context(),
            "filter_dict": filter_dict,
            "filter": filter,
            "pk": pk,
            "create": create,
        }
        template = (
            "geant/filters/_filter_edit_content.html"
            if request.htmx
            else "geant/filters/filter_list.html"
        )
        return render(request, template, context=context)

    if request.method == "POST":
        if not request.htmx:
            return HttpResponseBadRequest("only htmx supported")
        filter_dict = update_filter(request.POST, request.GET)
        context = {
            **default_edit_context(),
            "filter_dict": filter_dict,
            "is_root": True,
        }
        return render(request, "geant/filters/_filter_item.html", context=context)

    if request.method == "DELETE":
        if not pk:
            return HttpResponseNotAllowed(permitted_methods=["HEAD", "GET", "POST"])
        filter = get_object_or_404(Filter, pk=pk)
        filter.delete()
        return HttpResponse(headers={"HX-Redirect": reverse("geant-filters:filter-list")})


@require_POST
def save_filter(request, pk: Optional[int] = None):
    result = parse_filter_form_data(request.POST)
    name = request.POST.get("name")
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        context = {
            **default_edit_context(),
            "errors": {"name": "Name can only contain letters, numbers, - or _"},
            "filter_dict": result,
            "name": name,
        }
        return render(request, "geant/filters/_filter_edit_form.html", context=context)
    user = request.user

    # WARNING: COMPLETE HACK FOR DEMO PURPOSES
    # TODO: Remove
    if not user.is_authenticated:
        user = User.objects.first()

    if pk is None:
        Filter(name=name, user=user, filter=result).save()
    else:
        filter = Filter.objects.get(pk=pk)
        filter.name = name
        filter.filter = result
        filter.save()
    return HttpResponse(headers={"HX-Redirect": reverse("geant-filters:filter-list")})


def update_filter(form_data, commands):
    filter_dict = parse_filter_form_data(form_data)

    if create_after := commands.get("create_after"):
        items, idx = _get_items_list(filter_dict, create_after)
        items.insert(idx + 1, FILTER_MODEL.default_rule())

    if delete := commands.get("delete"):
        items, idx = _get_items_list(filter_dict, delete)
        if len(items) > 1:
            items.pop(idx)

    if move_up := commands.get("move_up"):
        items, idx = _get_items_list(filter_dict, move_up)
        if idx > 0:
            item = items.pop(idx)
            items.insert(idx - 1, item)

    if move_down := commands.get("move_down"):
        items, idx = _get_items_list(filter_dict, move_down)
        if idx < len(items) - 1:
            item = items.pop(idx)
            items.insert(idx + 1, item)
    return filter_dict


def _get_items_list(filter_dict: dict, location: str) -> tuple[list, int]:
    path = [int(i) for i in location.rstrip("_").split("_")]
    return _get_items_list_helper(filter_dict, path)


def _get_items_list_helper(filter_item: dict, path: list[int]):
    if len(path) == 1:
        return filter_item["items"], path[0]
    return _get_items_list_helper(filter_item["items"][path[0]], path[1:])


def parse_filter_form_data(form_data):
    return FILTER_MODEL.parse_form_data(form_data)
