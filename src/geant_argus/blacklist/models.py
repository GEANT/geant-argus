from argus.incident.constants import Level
from argus.notificationprofile.models import Filter as ArgusFilter
from django.contrib.auth import get_user_model
from django.db import models

from geant_argus.filter.model import filter_to_text
from geant_argus.geant_argus.incidents.severity import IncidentSeverity

User = get_user_model()


class Filter(ArgusFilter):
    class Meta:
        proxy = True

    @property
    def text(self):
        return filter_to_text(self.filter)

    def __str__(self):
        return self.name


class BlacklistManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("filter")


class Blacklist(models.Model):
    LEVEL_CHOICES = tuple((item.value, item.name) for item in IncidentSeverity)

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="blacklists")
    name = models.CharField(max_length=120, unique=True)
    message = models.CharField(max_length=255)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=max(Level).value)
    filter = models.ForeignKey(to=Filter, on_delete=models.CASCADE, related_name="blacklists")
    priority = models.IntegerField(db_default=10, default=10)
    enabled = models.BooleanField(db_default=True, default=True)
    review_date = models.DateField(blank=True, null=True)
    hidden = models.BooleanField(db_default=False, default=False)

    objects = BlacklistManager()

    @property
    def severity(self):
        return IncidentSeverity(self.level).name

    @property
    def filtertext(self):
        return self.filter.text
