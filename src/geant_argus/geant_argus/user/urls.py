from django.urls import path

from . import views


app_name = "geant_argus"
urlpatterns = [
    path("aural_alert/change/", views.change_aural_alert, name="change-aural-alert"),
]
