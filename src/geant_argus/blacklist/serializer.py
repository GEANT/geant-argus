from rest_framework import serializers
from .models import Blacklist


class BlacklistSerializer(serializers.ModelSerializer):
    severity = serializers.CharField()
    blacklist_version = serializers.SerializerMethodField()

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
            "blacklist_version",
        )

    def get_blacklist_version(self, obj):
        return 2


class CreateBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blacklist
        exclude = ("user",)
