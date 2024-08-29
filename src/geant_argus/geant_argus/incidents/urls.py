from django.urls import path

from . import views

app_name = "geant-incidents"
urlpatterns = [
    path("<int:pk>/ack", views.acknowledge_incident, name="ack-incident"),
    path("<int:pk>/begin-comment", views.begin_comment, name="begin-comment"),
]
