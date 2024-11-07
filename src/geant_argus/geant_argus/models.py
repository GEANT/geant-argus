from django.db import models
from argus.incident.constants import Level
from argus.notificationprofile.models import Filter

from geant_argus.geant_argus.incidents.severity import IncidentSeverity

Filter.__str__ = lambda self: self.name


class Blacklist(models.Model):
    LEVEL_CHOICES = tuple((item.value, item.name) for item in IncidentSeverity)

    name = models.CharField(max_length=120)
    message = models.CharField(max_length=255)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=max(Level).value)
    filter = models.ForeignKey(to=Filter, on_delete=models.CASCADE, related_name="blacklists")
