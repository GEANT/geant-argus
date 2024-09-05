from argus.site.urls import urlpatterns as argus_urlpatterns
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="incidents/", permanent=False), name="home"),
    *argus_urlpatterns,
    path("geant/incidents/", include("geant_argus.geant_argus.incidents.urls")),
    path("geant/status/", include("geant_argus.geant_argus.status.urls")),
    path("filters/", include("geant_argus.geant_argus.filters.urls")),
    path("", include("argus_htmx.urls")),
]
