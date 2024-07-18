from django.urls import path

from . import views


app_name = "geant"
urlpatterns = [
    path("", views.edit_filter, name="create-filter"),
    path("<int:pk>/", views.edit_filter, name="edit-filter"),
    path("<int:pk>/save/", views.save_filter, name="save-filter"),
]
