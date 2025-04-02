import pkg_resources
from django.http import HttpRequest, JsonResponse
from django.urls import path
from django.views.decorators.http import require_GET


def get_version_or_none(package):
    try:
        return pkg_resources.get_distribution(package).version
    except pkg_resources.DistributionNotFound:
        return None


@require_GET
def version(request: HttpRequest):
    return JsonResponse(
        {
            "dashboard-v3-python": get_version_or_none("dashboard-v3-python"),
            "django": get_version_or_none("django"),
            "geant-argus": get_version_or_none("geant-argus"),
        }
    )


urlpatterns = [
    path("version/", version, name="version"),
]
