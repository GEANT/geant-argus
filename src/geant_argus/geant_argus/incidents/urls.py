from django.urls import path

from . import views

app_name = "geant-incidents"
urlpatterns = [
    path("<int:pk>/update", views.update_incident, name="update-incident"),
]
