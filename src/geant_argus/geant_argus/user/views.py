# from argus.auth.utils import save_preference
from argus.htmx.incident.views import HtmxHttpRequest
from argus.auth.utils import get_or_update_preference
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRefresh


@require_POST
def change_aural_alert(request: HtmxHttpRequest) -> HttpResponse:
    get_or_update_preference(request, request.POST, "geant_argus", "aural_alert")

    return HttpResponseClientRefresh()
