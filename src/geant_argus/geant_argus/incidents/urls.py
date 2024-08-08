from django.urls import path

from . import views

app_name = "geant"
urlpatterns = [
    path("<int:pk>/ack", views.acknowledge_incident, name="ack-incident"),
]
