from django import forms

from argus.auth.models import preferences


class AuralAlertForm(forms.Form):
    aural_alert = forms.ChoiceField(required=False, choices=[("off", "off"), ("on", "on")])


@preferences(namespace="geant_argus")
class ArgusHtmxPreferences:
    FORMS = {
        "aural_alert": AuralAlertForm,
    }
    _FIELD_DEFAULTS = {
        "aural_alert": "off",
    }
