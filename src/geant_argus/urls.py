from argus.site.urls import urlpatterns
from django.urls import include, path
from geant_argus.geant_argus.filters import urls as filters_urls

urlpatterns += [
    path("filters/", include(filters_urls)),
    path("", include("argus_htmx.urls")),
]
