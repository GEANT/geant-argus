from argus.site.urls import urlpatterns
from django.urls import include, path

urlpatterns += [
    path("", include("argus_htmx.urls")),
]
