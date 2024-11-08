from django.urls import path

from . import views


app_name = "geant-blacklists"
urlpatterns = [
    path("", views.list_blacklists, name="blacklist-list"),
    path("new/", views.edit_blacklist, name="edit-blacklist"),
    path("<int:pk>/", views.edit_blacklist, name="edit-blacklist"),
    path("filter/", views.edit_filter, name="edit-filter"),
    path("filter/save", views.save_filter, name="save-filter"),
]
