from django import forms

from argus.auth.models import preferences, PreferenceField
from django.conf import settings


AURAL_ALERT_LIST = settings.NEW_INCIDENT_AURAL_ALERTS
AURAL_ALERT_DEFAULT = settings.NEW_INCIDENT_AURAL_ALERT_DEFAULT
AURAL_ALERT_CHOICES = tuple((ps, ps) for ps in AURAL_ALERT_LIST)


class AuralAlertForm(forms.Form):
    aural_alert = forms.ChoiceField(required=False, choices=AURAL_ALERT_CHOICES)


@preferences(namespace="geant_argus")
class GeantArgusPreferences:
    FIELDS = {
        "aural_alert": PreferenceField(
            form=AuralAlertForm, default=AURAL_ALERT_DEFAULT, choices=AURAL_ALERT_LIST
        )
    }
