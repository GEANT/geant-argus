from argus.filter.default import (  # noqa: F401
    ComplexFallbackFilterWrapper,
    validate_jsonfilter,
    FilterSerializer as DefaultFilterSerializer,
    QuerySetFilter,
    IncidentFilter as DefaultIncidentFilter,
    SourceLockedIncidentFilter,
    INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS,
    SOURCE_LOCKED_INCIDENT_OPENAPI_PARAMETER_DESCRIPTIONS,
)
from rest_framework import serializers


class FilterBlobSerializer(serializers.JSONField):
    def validate(self, data):
        return data


class FilterSerializer(DefaultFilterSerializer):
    filter = FilterBlobSerializer(required=True)


class IncidentFilter(DefaultIncidentFilter):
    pass
