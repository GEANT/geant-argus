import itertools
import json
from typing import Optional
from django import forms
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_http_methods

FIELDS = ["field_1", "field_2"]
OPERATORS = ["equals", "not_equals"]
FILTER = {
    "type": "group",
    "operator": "and",
    "items": [
        {
            "type": "group",
            "operator": "or",
            "items": [
                {
                    "type": "rule",
                    "field": "field_2",
                    "operator": "equals",
                    "value": "some other value",
                }
            ],
        },
    ],
}


class UpdateFilterForm(forms.Form):
    entry = forms.CharField(required=True)
    action = forms.ChoiceField(
        choices=[("set_op", "set_op"), ("create_after", "create_after"), ("delete", "delete")],
        required=True,
    )
    value = forms.CharField()


@require_http_methods(["HEAD", "GET", "POST"])
def edit_filter(request, pk: Optional[int] = None):
    if request.method == "POST":
        return update_filter_editor(request)

    context = {"fields": FIELDS, "operators": OPERATORS, "filter": {}}
    return render(request, "geant/filters/filter_edit.html", context=context)


@require_POST
def update_filter_editor(request):
    if not request.htmx:
        return HttpResponseBadRequest("only htmx supported")
    filter_dict = parse_filter_form_data(request.POST)
    data = request.GET
    print(data, request.POST, filter_dict)

    if create_after := data.get("create_after"):
        items, idx = _get_items_list(filter_dict, create_after)
        items.insert(idx + 1, {})

    if delete := data.get("delete"):
        items, idx = _get_items_list(filter_dict, delete)
        if len(items) > 1:
            items.pop(idx)

    context = {
        "fields": FIELDS,
        "operators": OPERATORS,
        "item": filter_dict,
        "is_root": True,
    }
    return render(request, "geant/filters/filter_item.html", context=context)

    if data["action"] == "set_op":
        return
    try:
        if not data["entry"]:
            items, idx = filter_dict, None
        else:
            path = [int(i) for i in data["entry"].split("_")]
            items, idx = _get_items_list(filter_dict, path)
        print(items, idx)
    except (ValueError, KeyError):
        return HttpResponseBadRequest(f"invalid entry {data.get('entry')}")
    if data["action"] == "set_op":
        if idx is None:
            update_item(items)
        else:
            items[idx] = update_item(items[idx])

    return render(request, "geant/filters/filter_edit.html", context=context)

    if data["action"] == "create_after":
        items.insert(idx + 1, {})
    return HttpResponse("success")
    # entry
    # action
    # value


def update_item(item: dict):
    if item["operator"] in ("and", "or") and item["type"] == "rule":
        item.clear()
        item.update({"type": "group", "operator": item["operator"], "items": [{}]})
    elif item["type"] == "group":
        item.clear()
        item.update({"type": "rule", "field": item["field"], "operator": "equals", "value": ""})


def _get_items_list(filter_dict: dict, location: str) -> tuple[list, int]:
    path = [int(i) for i in location.rstrip("_").split("_")]
    return _get_items_list_helper(filter_dict, path)


def _get_items_list_helper(filter_item: dict, location: list[int]):
    if len(location) == 1:
        return filter_item["items"], location[0]
    return _get_items_list_helper(filter_item["items"][location[0]], location[1:])


@require_POST
def save_filter(request, pk: Optional[int] = None):
    if pk is None:
        print("creating filter")
    else:
        print(f"updating filter for {pk}")

    result = parse_filter_form_data(request.POST)
    return HttpResponse(json.dumps(result), content_type="text/plain")


def parse_filter_form_data(form_data, prefix=""):
    if value := form_data.get(prefix + "field"):
        if value in ("or", "and"):
            return {"type": "group", "operator": value, "items": [{}]}
        return {
            "type": "rule",
            "field": value,
            "operator": form_data.get(prefix + "op", "equals"),
            "value": form_data.get(prefix + "val", ""),
        }

    if value := form_data.get(prefix + "op"):
        if value not in ("or", "and"):
            return {
                "type": "rule",
                "field": value,
                "operator": "equals",
                "value": "",
            }
        result = {"type": "group", "operator": value, "items": []}
        for idx in itertools.count():
            new_prefix = f"{prefix}{idx}_"
            parsed = parse_filter_form_data(form_data, prefix=new_prefix)
            if parsed is None:
                break
            result["items"].append(parsed)
        return result
    return None
