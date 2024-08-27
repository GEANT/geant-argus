import functools
import operator
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
from django import forms
from django.db.models import Q, QuerySet
from django.db.models.functions import Now
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from rest_framework import fields, serializers
from rest_framework.filters import BaseFilterBackend

from geant_argus.geant_argus.filters.schema import FILTER_SCHEMA_V1
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
        form = IncidentFilterForm(request.GET or {"open": True, "min_severity": 4})
        return form, form.filter_queryset(queryset)

    def filter_queryset(self, request, queryset, view=None):
        return IncidentFilterForm(request.GET or None).filter_queryset(queryset)


class GeantBooleanFiltering:
    FILTER_FIELD_MAPPING = {"description": "metadata__description"}

    def __init__(self, filter: Filter):
        self.filter_dict = filter.filter
        assert self.filter_dict["version"] == "v1", "unsupported filter version"

    def filter(self, qs: QuerySet) -> QuerySet:
        return qs.filter(self._parse_item(self.filter_dict))

    def _parse_item(self, item: dict):
        if item["type"] == "group":
            return self._parse_group(item)
        if item["type"] == "rule":
            return self._parse_rule(item)
        raise ValueError("invalid item type")

    def _parse_group(self, group: dict):
        op = operator.ior if group["operator"] == "or" else operator.iand
        return functools.reduce(op, (self._parse_item(i) for i in group["items"]))

    def _parse_rule(self, rule: dict):
        db_field = self.FILTER_FIELD_MAPPING[rule["field"]]
        if rule["operator"] == "equals":
            return Q(**{db_field: rule["value"]})
        if rule["operator"] == "contains":
            return Q(**{f"{db_field}__icontains": rule["value"]})


class IncidentFilterForm(forms.Form):
    open = forms.BooleanField(required=False)
    closed = forms.BooleanField(required=False)
    description = forms.CharField(max_length=255, required=False)
    newest_first = forms.BooleanField(required=False)
    min_severity = forms.ChoiceField(
        required=False, choices=[(s.value, s.name) for s in IncidentSeverity]
    )
    field_order = ["open", "closed", "description", "filter_pk", "min_severity", "newest_first"]

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
        queryset = self._filter_by_open_close(queryset)
        queryset = self._filter_by_description(queryset)
        queryset = self._filter_by_severity(queryset)
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
        return GeantBooleanFiltering(filter).filter(queryset)

    def _filter_by_open_close(self, queryset):
        is_open = bool(self.cleaned_data.get("open"))
        is_closed = bool(self.cleaned_data.get("closed"))

        if not (is_open ^ is_closed):
            return queryset
        q = Q(end_time__isnull=False, end_time__gt=Now())
        if is_closed:
            q = ~q
        return queryset.filter(q)

    def _filter_by_description(self, queryset):
        if not (description := self.cleaned_data.get("description")):
            return queryset
        return queryset.filter(metadata__description__icontains=description)

    def _filter_by_severity(self, queryset):
        if not (level := self.cleaned_data.get("min_severity")):
            return queryset
        return queryset.filter(level__lte=level)

    def _order_by_newest_first(self, queryset):
        if self.cleaned_data.get("newest_first"):
            return queryset.order_by("-start_time")
        # Here we are lucky that statuses 'active', 'clear', 'closed' are alphabetically
        # in that order, so it's easy to sort
        return queryset.order_by("metadata__status", "level", "-start_time")


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
