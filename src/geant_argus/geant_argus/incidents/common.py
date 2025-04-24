from django import forms


class EmptyStringAllowedCharField(forms.CharField):
    empty_values = (None,)  # empty string '' should not be considered an empty value
