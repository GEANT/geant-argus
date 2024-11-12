from django.db import models
from argus.incident.constants import Level
from argus.notificationprofile.models import Filter

from geant_argus.geant_argus.incidents.severity import IncidentSeverity


# We should probably do this fancier with a subclass that's Meta.proxy=True
Filter.__str__ = lambda self: self.name


class BlacklistManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("filter")


class Blacklist(models.Model):
    LEVEL_CHOICES = tuple((item.value, item.name) for item in IncidentSeverity)

    name = models.CharField(max_length=120)
    message = models.CharField(max_length=255)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=max(Level).value)
    filter = models.ForeignKey(to=Filter, on_delete=models.CASCADE, related_name="blacklists")

    objects = BlacklistManager()
