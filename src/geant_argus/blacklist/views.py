from rest_framework import viewsets, permissions

from geant_argus.blacklist.models import Blacklist
from geant_argus.blacklist.serializer import BlacklistSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(description="List Blacklists", responses=BlacklistSerializer)
)
class BlacklistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Blacklist.objects.all().order_by("id")
    serializer_class = BlacklistSerializer
    permission_classes = [permissions.IsAuthenticated]
