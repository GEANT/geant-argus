from django.urls import path

from . import views

app_name = "geant-status"
urlpatterns = [
    path("", views.service_status, name="status"),
]
