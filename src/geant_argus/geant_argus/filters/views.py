from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_safe, require_POST

FIELDS = ["field 1", "field 2"]
OPERATORS = ["equals", "not_equals"]
SIMPLE_FILTER = {
    "type": "rule",
    "field": "field 1",
    "operator": "equals",
    "value": "some value",
}
FILTER_GROUP = {
    "type": "group",
    "operator": "and",
    "items": [
        SIMPLE_FILTER,
        {
            "type": "rule",
            "field": "field 2",
            "operator": "equals",
            "value": "some other value",
        },
    ],
}


@require_safe
def edit_filter(request):
    context = {"fields": FIELDS, "operators": OPERATORS, "filter": SIMPLE_FILTER}
    return render(request, "geant/filters/filter_edit.html", context=context)


@require_POST
def update_filter_editor(request):
    if not request.htmx:
        raise HttpResponseBadRequest("only htmx supported")


@require_POST
def save_filter():
    pass


def render_filter_builder():
    filterblob = [  # noqa: F841
        "and",
        [
            "or",
            [{"field": "some field", "operator": "equals", "value": "some value"}],
        ],
    ]
    form_data = {  # noqa: F841
        "0": "and",
        "1_0": "or",
        "1_1_field": "some field",
        "1_1_op": "eq",
        "1_1_val": "some value",
    }
