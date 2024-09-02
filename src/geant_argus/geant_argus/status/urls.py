from django.urls import path

from . import views

app_name = "geant-status"
urlpatterns = [
    path("", views.service_status, name="status"),
    path("/update", views.update_inventory, name="update"),
]
