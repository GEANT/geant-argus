from enum import IntEnum
import json
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


class IncidentSeverity(IntEnum):
    """Reverse from dashboard.correlation.enums.AlarmSeverity"""

    CRITICAL = 1
    MAJOR = 2
    MINOR = 3
    WARNING = 4
    HIDE = 5


@register.filter(name="to_severity")
def level_to_severity(value):
    """Removes all values of arg from the given string"""
    min_level = min(IncidentSeverity)
    max_level = max(IncidentSeverity)
    level = max(min_level, min(max_level, value))
    return IncidentSeverity(level).name


@register.filter(name="json_pp")
def json_pp(value):
    """pretty formats as json if possible"""
    try:
        return json.dumps(value, indent=2)
    except TypeError:
        return value


@register.filter
@stringfilter
def upperfirst(value: str):
    if not value:
        return ""
    return value[0].upper() + value[1:].lower()
