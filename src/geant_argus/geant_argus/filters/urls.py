from django.urls import path

from . import views


app_name = "geant-filters"
urlpatterns = [
    path("", views.list_filters, name="filter-list"),
    path("run/", views.run_filter, name="run-filter"),
    path("clear/", views.clear_temporary_filter, name="clear-filter"),
    path("new/save/", views.save_filter, name="save-new-filter"),
    path("new/", views.edit_filter, name="edit-filter"),
    path("<int:pk>/", views.edit_filter, name="edit-filter"),
    path("<int:pk>/save/", views.save_filter, name="save-filter"),
    path("<int:pk>run/", views.run_filter, name="run-filter"),
    path("filter-text/", views.get_filter_text, name="filter-text"),
]
