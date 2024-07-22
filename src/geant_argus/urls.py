from argus.site.urls import urlpatterns
from django.urls import include, path
from . import views

urlpatterns += [
    path("", include("argus_htmx.urls")),
    path('modal/', views.modal_view, name='modal-view'),
]
