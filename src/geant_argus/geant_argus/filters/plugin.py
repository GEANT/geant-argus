from typing import Any, Dict
from argus.filter.default import (  # noqa: F401
    ComplexFallbackFilterWrapper,
    FilterSerializer as DefaultFilterSerializer,
    QuerySetFilter,
    IncidentFilter as DefaultIncidentFilter,
    SourceLockedIncidentFilter,
    INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS,
    SOURCE_LOCKED_INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS,
)
from drf_spectacular.openapi import AutoSchema
import jsonschema
from rest_framework import serializers, fields
from drf_spectacular.extensions import OpenApiSerializerExtension
from geant_argus.geant_argus.filters.schema import FILTER_SCHEMA_V1

from django.template import loader
from argus.filter.filters import Filter


class _FilterBlobSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        data = fields.JSONField(required=self.required).to_internal_value()
        try:
            jsonschema.validate(data, schema=FILTER_SCHEMA_V1)
        except jsonschema.ValidationError as e:
            raise serializers.ValidationError({e.json_path.replace("$", "filter", 1): e.message})
        return data

    def to_representation(self, instance):
        # dump data transparently
        return instance


class GeantFilterBackend:
    form_template = "geant.filters._select_filter_by_name.html"

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

    @classmethod
    def incident_list_filter(cls, request, qs):

        return cls.to_html(request), qs

    @classmethod
    def to_html(cls, request):
        template = loader.get_template(cls.template)
        context = {"filters": Filter.objects.filter("")}
        return template.render(context, request)


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


validate_jsonfilter = GeantFilterBackend.validate_jsonfilter
FilterSerializer = GeantFilterBackend.get_filter_serializer()
FilterBlobSerializer = GeantFilterBackend.get_filter_blob_serializer()
IncidentFilter = GeantFilterBackend.get_incident_filter()

incident_list_filter = GeantFilterBackend.incident_list_filter
