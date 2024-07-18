from argus.site.urls import urlpatterns
from django.urls import include, path

urlpatterns += [
    path("filters/", include("geant_argus.geant_argus.filters.urls")),
    path("", include("argus_htmx.urls")),
]
