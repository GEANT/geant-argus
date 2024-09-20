from django import template
from django.utils.dateparse import parse_datetime

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def dateparse(datestr):
    return parse_datetime(datestr)
