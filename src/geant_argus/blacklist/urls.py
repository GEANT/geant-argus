from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"blacklists", views.BlacklistViewSet)
user_blacklist_list = views.MyBlacklistViewset.as_view({"get": "list"})


app_name = "blacklist"

urlpatterns = [
    path("blacklists/mine/", user_blacklist_list, name="my_blacklists"),
    path("", include(router.urls)),
]
