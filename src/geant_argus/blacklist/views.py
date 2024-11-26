from rest_framework import permissions

from geant_argus.blacklist.models import Blacklist
from geant_argus.blacklist.serializer import BlacklistSerializer, CreateBlacklistSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_rw_serializers import viewsets as rw_viewsets
from argus.notificationprofile.views import FilterViewSet as ArgusFilterViewSet, Filter


@extend_schema_view(
    list=extend_schema(description="List Blacklists", responses=BlacklistSerializer),
    retrieve=extend_schema(description="Get Blacklist", responses=BlacklistSerializer),
    create=extend_schema(
        description="Create Blacklist",
        request=CreateBlacklistSerializer,
        responses=BlacklistSerializer,
    ),
    update=extend_schema(
        description="Update Blacklist",
        request=CreateBlacklistSerializer,
        responses=BlacklistSerializer,
    ),
    destroy=extend_schema(description="Delete Blacklist"),
)
class BlacklistViewSet(rw_viewsets.ModelViewSet):
    """
    API endpoint that allows blacklists to be viewed or edited.
    """

    queryset = Blacklist.objects.all().order_by("id")
    serializer_class = BlacklistSerializer
    permission_classes = [permissions.IsAuthenticated]
    read_serializer_class = BlacklistSerializer
    write_serializer_class = CreateBlacklistSerializer


class FilterViewSet(ArgusFilterViewSet):
    """
    API endpoint that allows filters to be viewed or edited.
    """

    def get_queryset(self):
        return Filter.objects.all().order_by("id")
