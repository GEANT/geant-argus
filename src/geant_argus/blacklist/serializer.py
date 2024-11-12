from rest_framework import serializers
from .models import Blacklist
from argus.filter.serializers import FilterSerializer


class BlacklistSerializer(serializers.ModelSerializer):
    filter = FilterSerializer()

    class Meta:
        model = Blacklist
        fields = [
            "pk",
            "name",
            "message",
            "level",
            "filter",
        ]
