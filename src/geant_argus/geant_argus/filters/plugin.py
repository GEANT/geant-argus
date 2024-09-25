from typing import Any, Dict

import jsonschema
from argus.filter.default import (  # noqa: F401
    INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS,
    SOURCE_LOCKED_INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS,
    ComplexFallbackFilterWrapper,
)
from argus.filter.default import FilterSerializer as DefaultFilterSerializer
from argus.filter.default import IncidentFilter as DefaultIncidentFilter
from argus.filter.default import QuerySetFilter, SourceLockedIncidentFilter  # noqa: F401
from argus.filter.filters import Filter
from argus.incident.models import Event
from django import forms
from django.db.models import OuterRef, Exists, Case, When, Value
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from rest_framework import fields, serializers
from rest_framework.filters import BaseFilterBackend

from .filters import FILTER_MODEL
from .schema import FILTER_SCHEMA_V1
from geant_argus.geant_argus.incidents.severity import IncidentSeverity

SUPPORTED_FILTER_VERSIONS = ["v1"]


class _FilterBlobSerializer(serializers.Serializer):
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


class GeantFilterBackend(BaseFilterBackend):
    template = "geant/filters/_select_filter_by_name.html"

    @classmethod
    def get_filter_blob_serializer(cls):
        return _FilterBlobSerializer

    @classmethod
    def validate_jsonfilter(cls, value: dict):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Filter is not a dict")
        if not value:
            return True
        serializer = cls.get_filter_blob_serializer()(data=value)
        if serializer.is_valid():
            return True
        raise serializers.ValidationError("Filter is not valid")

    @classmethod
    def get_filter_serializer(cls):
        class FilterSerializer(DefaultFilterSerializer):
            filter = cls.get_filter_blob_serializer()(required=True)

        return FilterSerializer

    @classmethod
    def get_incident_filter(cls):
        class IncidentFilter(DefaultIncidentFilter):
            pass

        return IncidentFilter

    def incident_list_filter(self, request, queryset):
        form = IncidentFilterForm(
            request.GET
            or {"status": ["active", "clear"], "min_severity": IncidentSeverity.WARNING.value},
        )
        return form, form.filter_queryset(queryset)

    def filter_queryset(self, request, queryset, view=None):
        return IncidentFilterForm(request.GET or None).filter_queryset(queryset)


class DaisyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "forms/daisy_multiple_select_checkbox.html"


class IncidentFilterForm(forms.Form):
    status = forms.MultipleChoiceField(
        required=False,
        choices=[("active", "Active"), ("clear", "Clear"), ("closed", "Closed")],
        widget=DaisyCheckboxSelectMultiple,
    )
    description = forms.CharField(max_length=255, required=False)
    min_severity = forms.ChoiceField(
        required=False, choices=[(s.value, s.name) for s in IncidentSeverity]
    )
    newest_first = forms.BooleanField(required=False)
    short_lived = forms.BooleanField(required=False)

    field_order = [
        "status",
        "description",
        "filter_pk",
        "min_severity",
        "newest_first",
        "short_lived",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["filter_pk"] = forms.ChoiceField(
            required=False,
            label="Filter",
            choices=[
                ("", "------"),
                *((f.pk, f.name) for f in Filter.objects.filter(filter__version="v1").all()),
            ],
        )
        self.order_fields(self.field_order)

    def filter_queryset(self, queryset):
        if not self.is_valid():
            return queryset

        queryset = self._filter_by_pk(queryset)
        queryset = self._filter_by_status(queryset)
        queryset = self._filter_by_short_lived(queryset)
        queryset = self._filter_by_description(queryset)
        queryset = self._filter_by_severity(queryset)
        queryset = self._annotate_acks(queryset)
        queryset = self._order_by_newest_first(queryset)
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

    def _filter_by_short_lived(self, queryset):
        if self.cleaned_data.get("short_lived"):
            return queryset.filter(metadata__short_lived=True)
        return queryset

    def _filter_by_description(self, queryset):
        if not (description := self.cleaned_data.get("description")):
            return queryset
        return queryset.filter(description__icontains=description)

    def _filter_by_severity(self, queryset):
        if not (level := self.cleaned_data.get("min_severity")):
            return queryset
        return queryset.filter(level__lte=level)

    def _annotate_acks(self, queryset):
        return queryset.annotate(
            any_ack=Case(
                When(metadata__status="CLOSED", then=Value(True)),
                default=Exists(Event.objects.filter(incident=OuterRef("pk"), type="ACK")),
            ),
            noc_ack=Exists(
                Event.objects.filter(
                    incident=OuterRef("pk"), type="ACK", actor__groups__name="noc"
                )
            ),
            servicedesk_ack=Exists(
                Event.objects.filter(
                    incident=OuterRef("pk"), type="ACK", actor__groups__name="servicedesk"
                )
            ),
        )

    def _order_by_newest_first(self, queryset):
        if self.cleaned_data.get("newest_first"):
            return queryset.order_by("-start_time")
        # Here we are lucky that statuses 'active', 'clear', 'closed' are alphabetically
        # in that order, so it's easy to sort
        return queryset.order_by("any_ack", "metadata__status", "level", "-start_time")


class _FilterBlobExtension(OpenApiSerializerExtension):
    """OpenAPI docs generator extension for the FilterBlob data type"""

    target_class = GeantFilterBackend.get_filter_blob_serializer()

    def get_name(self, auto_schema: AutoSchema, direction) -> str | None:
        return "FilterBlob"

    def map_serializer(self, auto_schema: AutoSchema, direction) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["rule", "group"], "example": "rule"},
                "operator": {"type": "string", "example": "equals"},
                "field": {"type": "string", "example": "description"},
                "value": {"type": "string", "example": "IP TRUNK"},
            },
        }


_backend = GeantFilterBackend()
validate_jsonfilter = _backend.validate_jsonfilter
FilterSerializer = _backend.get_filter_serializer()
FilterBlobSerializer = _backend.get_filter_blob_serializer()
IncidentFilter = _backend.get_incident_filter()

incident_list_filter = _backend.incident_list_filter
