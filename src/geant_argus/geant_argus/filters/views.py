import re
from typing import Optional

from argus.incident.models import User
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from geant_argus.blacklist.models import Blacklist, Filter
from geant_argus.geant_argus.view_helpers import redirect

from .filters import FILTER_MODEL, filter_to_text

PER_PAGE = 20


def get_all_filters():
    return Filter.objects.select_related("user")


@require_GET
def list_filters(request):
    # Load incidents
    qs = (
        get_all_filters()
        .filter(~Exists(Blacklist.objects.filter(filter=OuterRef("pk"))))
        .order_by("name")
    )
    # Standard Django pagination
    page_num = request.GET.get("page", "1")
    page = Paginator(object_list=qs, per_page=PER_PAGE).get_page(page_num)

    # The htmx magic - use a different, minimal base template for htmx
    # requests, allowing us to skip rendering the unchanging parts of the
    # template.
    if request.htmx:
        base_template = "geant/filters/_filter_table.html"
    else:
        base_template = "geant/filters/filter_list.html"

    context = {
        "column_count": 3,
        "count": qs.count(),
        "page_title": "Filters",
        "page": page,
    }

    return render(request, base_template, context=context)


def default_context():
    return {"name": "", "model": FILTER_MODEL}


def render_edit_filter(request, template, pk: Optional[int] = None, context=None):
    context = context or {}
    if pk:
        filter = get_object_or_404(Filter, pk=pk)
        filter_dict = FILTER_MODEL.upgrade_simple_filter(filter.filter)
    else:
        filter = None
        filter_dict = FILTER_MODEL.default_group()
    context = {
        **default_context(),
        "filter_dict": filter_dict,
        "filter": filter,
        "pk": pk,
        **context,
    }
    return render(request, template, context=context)


@require_POST
def get_filter_text(request):
    filter_dict = parse_filter_form_data(request.POST)
    filter_text = filter_to_text(filter_dict)
    return HttpResponse(filter_text)


@require_http_methods(["HEAD", "GET", "POST", "DELETE"])
def edit_filter(request, pk: Optional[int] = None):
    if request.method == "GET":
        template = (
            "geant/filters/_filter_edit_content.html"
            if request.htmx
            else "geant/filters/filter_edit.html"
        )
        return render_edit_filter(request, template, pk)

    if request.method == "POST":
        if not request.htmx:
            return HttpResponseBadRequest("only htmx supported")
        filter_dict = parse_filter_form_data(request.POST)
        filter_dict = update_filter(filter_dict, request.GET)
        context = {
            **default_context(),
            "filter_dict": filter_dict,
            "is_root": True,
        }
        return render(request, "geant/filters/_filter_root.html", context=context)

    if request.method == "DELETE":
        if not pk:
            return HttpResponseNotAllowed(permitted_methods=["HEAD", "GET", "POST"])
        filter = get_object_or_404(Filter, pk=pk)
        filter.delete()
        return HttpResponse(headers={"HX-Redirect": reverse("geant-filters:filter-list")})


@require_POST
def save_filter(request, pk: Optional[int] = None):
    result = save_filter_from_request(request, pk)
    if isinstance(result, HttpResponse):
        # result may be an error response
        return result
    return HttpResponse(headers={"HX-Redirect": reverse("geant-filters:filter-list")})


@require_POST
def store_temporary_filter(request):
    result = parse_filter_form_data(request.POST)
    if result:
        request.session["temporary_filter"] = result
    return redirect(request, "htmx:incident-list")


@require_POST
def clear_temporary_filter(request):
    request.session.pop("temporary_filter")
    return redirect(request, "htmx:incident-list")


def save_filter_from_request(request, pk: Optional[int] = None):
    result = parse_filter_form_data(request.POST)
    name = request.POST.get("name")
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        context = {
            **default_context(),
            "errors": {"name": "Name can only contain letters, numbers, - or _"},
            "filter_dict": result,
            "name": name,
            "edit_url": reverse("geant-filters:edit-filter", args=(pk,) if pk else ()),
        }
        response = render(request, "geant/filters/_filter_edit_form.html", context=context)
        response.headers["HX-Retarget"] = "#filter-form"
        response.headers["HX-Reswap"] = "outerHTML"
        return response
    user = request.user

    # WARNING: COMPLETE HACK FOR DEMO PURPOSES
    # TODO: Remove
    if not user.is_authenticated:
        user = User.objects.first()

    if pk is None:
        filter = Filter(name=name, user=user, filter=result)
    else:
        filter = Filter.objects.get(pk=pk)
        filter.name = name
        filter.filter = result
    filter.save()
    return filter


def update_filter(filter_dict, commands):
    if create_after := commands.get("create_after"):
        if create_after == "root" and filter_dict["type"] == "rule":
            filter_dict.pop("version", None)
            filter_dict = FILTER_MODEL.with_version(
                FILTER_MODEL.default_group(items=[filter_dict, FILTER_MODEL.default_rule()])
            )

        else:
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
