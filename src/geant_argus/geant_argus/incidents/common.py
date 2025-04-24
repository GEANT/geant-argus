from django import forms
from django.core import validators

from django.utils.regex_helper import _lazy_re_compile


class EmptyStringAllowedCharField(forms.CharField):
    empty_values = (None,)  # empty string '' should not be considered an empty value


class TicketRefField(forms.CharField):
    default_validators = (
        validators.RegexValidator(
            _lazy_re_compile(r"^\d{0,16}\Z"),
            message="Enter a valid ticket number.",
            code="invalid",
        ),
    )
    empty_values = (None,)  # empty string '' should not be considered an empty value
