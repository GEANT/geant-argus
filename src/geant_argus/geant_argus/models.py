from django import forms

from argus.auth.models import preferences, PreferenceField


class AuralAlertForm(forms.Form):
    aural_alert = forms.ChoiceField(required=False, choices=[("off", "off"), ("on", "on")])


@preferences(namespace="geant_argus")
class GeantArgusPreferences:
    FIELDS = {"aural_alert": PreferenceField(form=AuralAlertForm, default="off")}
