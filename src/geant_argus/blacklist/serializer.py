from rest_framework import serializers
from .models import Blacklist
from argus.filter.serializers import FilterBlobSerializer


class BlacklistFilterField(serializers.RelatedField):
    def to_representation(self, value):
        return FilterBlobSerializer().to_representation(value.filter)


class BlacklistSerializer(serializers.ModelSerializer):
    filter = BlacklistFilterField(read_only=True)
    severity = serializers.CharField()

    class Meta:
        model = Blacklist
        fields = (
            "pk",
            "name",
            "level",
            "severity",
            "message",
            "filter",
        )
