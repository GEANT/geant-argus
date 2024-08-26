from argus.site.urls import urlpatterns as argus_urlpatterns
from django.urls import include, path
from geant_argus.geant_argus.filters import urls as filter_urls
from geant_argus.geant_argus.incidents import urls as incident_urls
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="incidents/", permanent=False)),
    *argus_urlpatterns,
    path("geant/incidents/", include(incident_urls)),
    path("filters/", include(filter_urls)),
    path("", include("argus_htmx.urls")),
]
