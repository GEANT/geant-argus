from typing import Optional
from django import template

from geant_argus.geant_argus.filters.filters import filter_to_text


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


register.filter(filter_to_text)
