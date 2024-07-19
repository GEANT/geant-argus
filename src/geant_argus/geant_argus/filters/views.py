import itertools
import json
from typing import Optional
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_http_methods

FIELDS = ["field_1", "field_2"]
OPERATORS = ["equals", "not_equals", "contains"]


@require_http_methods(["HEAD", "GET", "POST"])
def edit_filter(request, pk: Optional[int] = None):
    if request.method == "POST":
        if not request.htmx:
            return HttpResponseBadRequest("only htmx supported")
        filter_dict = update_filter(request.POST, request.GET)
        context = {
            "fields": FIELDS,
            "operators": OPERATORS,
            "filter": filter_dict,
            "is_root": True,
        }
        return render(request, "geant/filters/filter_item.html", context=context)
    context = {"fields": FIELDS, "operators": OPERATORS, "filter": default_filter()}
    return render(request, "geant/filters/filter_edit.html", context=context)


@require_POST
def save_filter(request, pk: Optional[int] = None):
    if pk is None:
        print("creating filter")
    else:
        print(f"updating filter for {pk}")

    result = parse_filter_form_data(request.POST)
    return HttpResponse(json.dumps(result), content_type="text/plain")


def update_filter(form_data, commands):
    filter_dict = parse_filter_form_data(form_data)

    if create_after := commands.get("create_after"):
        items, idx = _get_items_list(filter_dict, create_after)
        items.insert(idx + 1, default_filter())

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


def default_filter():
    return {"type": "rule", "field": FIELDS[0], "operator": OPERATORS[0], "value": ""}


def _get_items_list(filter_dict: dict, location: str) -> tuple[list, int]:
    path = [int(i) for i in location.rstrip("_").split("_")]
    return _get_items_list_helper(filter_dict, path)


def _get_items_list_helper(filter_item: dict, location: list[int]):
    if len(location) == 1:
        return filter_item["items"], location[0]
    return _get_items_list_helper(filter_item["items"][location[0]], location[1:])


def parse_filter_form_data(form_data, prefix=""):
    if value := form_data.get(prefix + "field"):
        if value in ("or", "and"):
            return {"type": "group", "operator": value, "items": [default_filter()]}
        if value not in FIELDS:
            value = FIELDS[0]
        return {
            "type": "rule",
            "field": value,
            "operator": form_data.get(prefix + "op", OPERATORS[0]),
            "value": form_data.get(prefix + "val", ""),
        }

    if (value := form_data.get(prefix + "op")) is not None:
        if value not in ("or", "and"):
            if value not in FIELDS:
                value = FIELDS[0]
            return {
                "type": "rule",
                "field": value,
                "operator": OPERATORS[0],
                "value": "",
            }
        result = {"type": "group", "operator": value, "items": []}
        for idx in itertools.count():
            new_prefix = f"{prefix}{idx}_"
            parsed = parse_filter_form_data(form_data, prefix=new_prefix)
            if parsed is None:
                break
            result["items"].append(parsed)
        if not result["items"]:
            result["items"].append(default_filter())
        return result
    return None
