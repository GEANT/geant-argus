from rest_framework import serializers
from .models import Blacklist
from argus.filter.serializers import FilterBlobSerializer


class BlacklistFilter(serializers.RelatedField):
    def to_representation(self, value):
        return FilterBlobSerializer().to_representation(value.filter)


class BlacklistSerializer(serializers.ModelSerializer):
    filter = BlacklistFilter(read_only=True)

    class Meta:
        model = Blacklist
        fields = [
            "pk",
            "name",
            "message",
            "level",
            "filter",
        ]
