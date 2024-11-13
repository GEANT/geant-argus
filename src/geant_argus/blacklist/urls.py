from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"blacklists", views.BlacklistViewSet)

app_name = "blacklist"

urlpatterns = [
    path("", include(router.urls)),
]
