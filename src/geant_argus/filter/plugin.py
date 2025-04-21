"""
Filter plugin used by Geant Argus, set using the ``ARGUS_FILTER_BACKEND`` and
``ARGUS_HTMX_FILTER_FUNCTION`` settings. Geant Argus overrides or provides custom implementations
for a number of the classes/functions that are used by Argus. These are


* FilterBlobSerializer
* incident_list_filter

Furthermore, this module passes through a number of required global attributes without
modification. These are:

* INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS
* SOURCE_LOCKED_INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS
* ComplexFallbackFilterWrapper
* IncidentFilter
* QuerySetFilter
* SourceLockedIncidentFilter
"""

from typing import Any, Dict

import jsonschema
from argus.filter.default import (
    INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS,
    SOURCE_LOCKED_INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS,
    ComplexFallbackFilterWrapper,
    IncidentFilter,
    QuerySetFilter,
    SourceLockedIncidentFilter,
)
from argus.filter.filters import Filter
from argus.incident.models import Event, IncidentQuerySet
from django import forms
from django.db.models import Case, Exists, OuterRef, Subquery, Value, When
from django.http import HttpRequest
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from rest_framework import fields, serializers

from geant_argus.geant_argus.incidents.severity import IncidentSeverity

from .model import FILTER_MODEL
from .schema import FILTER_SCHEMA_V1

__all__ = (
    "INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS",
    "SOURCE_LOCKED_INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS",
    "ComplexFallbackFilterWrapper",
    "IncidentFilter",
    "QuerySetFilter",
    "SourceLockedIncidentFilter",
    "FilterBlobSerializer",
    "default_filter_params",
    "incident_list_filter",
)

SUPPORTED_FILTER_VERSIONS = ["v1"]


def incident_list_filter(request, queryset):
    form = IncidentFilterForm(
        request.GET or default_filter_params(),
    )
    queryset = form.filter_queryset(queryset, request)
    _update_session(request, queryset)
    return form, queryset


def default_filter_params():
    return {"status": ["active", "clear"], "min_severity": IncidentSeverity.WARNING.value}


def _update_session(request: HttpRequest, queryset: IncidentQuerySet):
    pending = set(
        incident.id for incident in queryset.open().filter(metadata__phase="PENDING").all()
    )
    old_pending = set(request.session.get("geant.pending_incidents", []))
    request.session["geant.pending_incidents"] = list(pending)
    request.session["geant.new_pending_incidents"] = list(pending - old_pending)


class DaisyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "forms/daisy_multiple_select_checkbox.html"


class IncidentFilterForm(forms.Form):
    status = forms.MultipleChoiceField(
        required=False,
        choices=[("active", "Active"), ("clear", "Clear"), ("closed", "Closed")],
        widget=DaisyCheckboxSelectMultiple,
    )

    alarm_id = forms.CharField(
        label="Alarm ID",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "max-w-32"}),
    )
    filter_pk = forms.ChoiceField(
        required=False,
        label="Filter",
        widget=forms.Select(attrs={"class": "max-w-52"}),
    )
    description = forms.CharField(max_length=255, required=False)
    description.in_header = True
    location = forms.CharField(max_length=255, required=False)
    location.in_header = True
    equipment = forms.CharField(max_length=255, required=False)
    equipment.in_header = True
    min_severity = forms.ChoiceField(
        required=False, choices=[(s.value, s.name) for s in IncidentSeverity]
    )
    newest_first = forms.BooleanField(required=False)
    short_lived = forms.BooleanField(required=False)
    description = forms.CharField(max_length=255, required=False)
    description.in_header = True
    location = forms.CharField(max_length=255, required=False)
    location.in_header = True
    equipment = forms.CharField(max_length=255, required=False)
    equipment.in_header = True

    ticket_ref = forms.CharField(max_length=255, required=False)
    ticket_ref.in_header = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["filter_pk"].choices = [
            ("", "------"),
            *((f.pk, f.name) for f in Filter.objects.filter(filter__version="v1").all()),
        ]

    def filter_queryset(self, queryset, request):
        self.request = request

        if not self.is_valid():
            return queryset

        queryset = self._annotate_acks(queryset)
        queryset = self._filter_by_session_filter(queryset)
        queryset = self._filter_by_pk(queryset)
        queryset = self._filter_by_status(queryset)
        queryset = self._filter_by_field(queryset, "description", "description__icontains")
        queryset = self._filter_by_field(queryset, "location", "metadata__location__icontains")
        queryset = self._filter_by_field(queryset, "equipment", "metadata__equipment__icontains")
        queryset = self._filter_by_field(queryset, "min_severity", "level__lte")
        queryset = self._filter_by_field(queryset, "alarm_id", "source_incident_id")
        queryset = self._filter_by_field(queryset, "ticket_ref", "metadata__ticket_ref__icontains")
        queryset = self._filter_by_short_lived(queryset)
        queryset = self._order_by_newest_first(queryset)
        return queryset

    def _filter_by_session_filter(self, queryset):
        if temp_filter := self.request.session.get("temporary_filter"):
            return FILTER_MODEL.filter_queryset(queryset, temp_filter)
        return queryset

    def _filter_by_pk(self, queryset):
        if not (filter_pk := self.cleaned_data.get("filter_pk")):
            return queryset
        filter = Filter.objects.get(pk=filter_pk)

        if not (
            filter and filter.filter and filter.filter.get("version") in SUPPORTED_FILTER_VERSIONS
        ):
            return queryset
        return FILTER_MODEL.filter_queryset(queryset, filter.filter)

    def _filter_by_status(self, queryset):
        status = [s.upper() for s in self.cleaned_data.get("status")]
        # short lived alarms are always closed, so we don't extra filter on open/closed
        if self.cleaned_data.get("short_lived"):
            return queryset
        return queryset.filter(metadata__status__in=status)

    def _filter_by_field(self, queryset, form_field, filter_kwarg):
        if not (value := self.cleaned_data.get(form_field)):
            return queryset
        return queryset.filter(**{filter_kwarg: value})

    def _filter_by_short_lived(self, queryset):
        if self.cleaned_data.get("short_lived"):
            return queryset.filter(metadata__short_lived=True)
        return queryset

    def _annotate_acks(self, queryset):
        return queryset.annotate(
            ack_or_closed=Case(
                When(metadata__status="CLOSED", then=Value(True)),
                default=Exists(Event.objects.filter(incident=OuterRef("pk"), type="ACK")),
            ),
            ack=Exists(Event.objects.filter(incident=OuterRef("pk"), type="ACK")),
            ack_user=Subquery(
                Event.objects.filter(incident=OuterRef("pk"), type="ACK")
                .order_by("-timestamp")
                .values("actor__username")[:1]
            ),
        )

    def _order_by_newest_first(self, queryset):
        if self.cleaned_data.get("newest_first"):
            return queryset.order_by("-start_time")
        # Here we are lucky that statuses 'active', 'clear', 'closed' are alphabetically
        # in that order, so it's easy to sort
        return queryset.order_by("ack_or_closed", "metadata__status", "level", "-start_time")


class FilterBlobSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        data = fields.JSONField(required=self.required).to_internal_value(data)
        try:
            jsonschema.validate(data, schema=FILTER_SCHEMA_V1)
        except jsonschema.ValidationError as e:
            raise serializers.ValidationError({e.json_path.replace("$", "filter", 1): e.message})
        return data

    def to_representation(self, instance):
        # dump data transparently
        return instance


class _FilterBlobExtension(OpenApiSerializerExtension):
    """OpenAPI docs generator extension for the FilterBlob data type"""

    target_class = FilterBlobSerializer

    def get_name(self, auto_schema: AutoSchema, direction) -> str | None:
        return "FilterBlob"

    def map_serializer(self, auto_schema: AutoSchema, direction) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["rule", "group"], "example": "rule"},
                "operator": {"type": "string", "example": "contains"},
                "field": {"type": "string", "example": "description"},
                "value": {"type": "string", "example": "IP TRUNK"},
            },
        }
