from django import template

from geant_argus.filters import filter_to_text
from .template_utils import concat, concat_underscore, is_multiple

register = template.Library()

register.filter(concat)
register.filter(concat_underscore)
register.filter(is_multiple)
register.filter(filter_to_text)
