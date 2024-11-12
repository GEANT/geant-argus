from argus.site.urls import urlpatterns as argus_urlpatterns
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="incidents/", permanent=False), name="home"),
    *argus_urlpatterns,
    path("oidc/", include("social_django.urls", namespace="social")),
    path("geant/incidents/", include("geant_argus.geant_argus.incidents.urls")),
    path("geant/status/", include("geant_argus.geant_argus.status.urls")),
    path("filters/", include("geant_argus.geant_argus.filters.urls")),
    path("blacklists/", include("geant_argus.geant_argus.blacklists.urls")),
    path("", include("argus_htmx.urls")),
    path("", include("geant_argus.blacklist.urls")),
]
