from django.db import models
from argus.incident.constants import Level
from argus.notificationprofile.models import Filter as ArgusFilter

from geant_argus.geant_argus.incidents.severity import IncidentSeverity


class Filter(ArgusFilter):
    class Meta:
        proxy = True

    def __str__(self):
        return self.name


class BlacklistManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("filter")


class Blacklist(models.Model):
    LEVEL_CHOICES = tuple((item.value, item.name) for item in IncidentSeverity)

    name = models.CharField(max_length=120, unique=True)
    message = models.CharField(max_length=255)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=max(Level).value)
    filter = models.ForeignKey(to=Filter, on_delete=models.CASCADE, related_name="blacklists")
    priority = models.IntegerField(db_default=10, default=10)
    enabled = models.BooleanField(db_default=True, default=True)
    review_date = models.DateField(blank=True, null=True)

    objects = BlacklistManager()

    @property
    def severity(self):
        return IncidentSeverity(self.level).name
