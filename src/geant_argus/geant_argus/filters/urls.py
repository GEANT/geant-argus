from django.urls import path

from . import views


app_name = "geant-filters"
urlpatterns = [
    path("", views.list_filters, name="filter-list"),
    path("new/", views.edit_filter, name="edit-filter"),
    path("new/save/", views.save_filter, name="save-new-filter"),
    path("<int:pk>/", views.edit_filter, name="edit-filter"),
    path("<int:pk>/save/", views.save_filter, name="save-filter"),
]
