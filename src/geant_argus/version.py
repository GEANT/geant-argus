from django.http import HttpRequest, JsonResponse
from django.urls import path
from django.views.decorators.http import require_GET
import importlib.metadata


def get_version_or_none(package):
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


@require_GET
def version(request: HttpRequest):
    return JsonResponse(
        {
            "argus": get_version_or_none("argus-server"),
            "dashboard-v3-python": get_version_or_none("dashboard"),
            "django": get_version_or_none("django"),
            "geant-argus": get_version_or_none("geant-argus"),
        }
    )


urlpatterns = [
    path("version/", version, name="version"),
]
