from typing import Optional
from django import template


register = template.Library()


@register.filter
def concat(first, second):
    return f"{first}{second}"


@register.filter
def concat_underscore(first, second):
    first = first or ""
    return f"{first}{second}_"


@register.filter
def is_multiple(arr: Optional[list]):
    if not arr:
        return False
    return len(arr) > 1


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def display_text(item):
    return {
        "description": "Description",
        "comment": "Comment",
        "location": "Location",
        "service_deck_ack": "Ack (SD)",
        "ncc_ack": "Ack (NOC)",
        "start_time": "Start Time",
        "before_abs": "before (absolute)",
        "after_abs": "after (absolute)",
        "before_rel": "before (relative)",
        "after_rel": "after (relative)",
    }.get(item, item)
