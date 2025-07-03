from rest_framework import serializers
from .models import Blacklist


class BlacklistSerializer(serializers.ModelSerializer):
    severity = serializers.CharField()

    class Meta:
        model = Blacklist
        depth = 1
        fields = (
            "pk",
            "name",
            "level",
            "severity",
            "message",
            "filter",
            "priority",
            "enabled",
            "review_date",
            "hidden",
        )


class CreateBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blacklist
        exclude = ("user",)
