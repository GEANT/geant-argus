from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"blacklists", views.BlacklistViewSet)

app_name = "blacklist"

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("api/v2/", include(router.urls)),
]
