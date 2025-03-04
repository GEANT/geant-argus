"""Contains views for the Argus api, for htmx views, see `geant_argus/geant_argus/blacklists`"""

from drf_rw_serializers import viewsets as rw_viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets

from geant_argus.blacklist.models import Blacklist
from geant_argus.blacklist.serializer import BlacklistSerializer, CreateBlacklistSerializer


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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(description="List My Blacklists", responses=BlacklistSerializer),
)
class MyBlacklistViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlacklistSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Blacklist.objects.none()

    def get_queryset(self):
        return self.request.user.blacklists.all()
