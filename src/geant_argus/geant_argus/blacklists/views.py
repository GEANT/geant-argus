from django.core.paginator import Paginator
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods

from geant_argus.geant_argus.models import Blacklist
from geant_argus.geant_argus.view_helpers import redirect


class CreateBlacklistForm(ModelForm):
    class Meta:
        model = Blacklist
        fields = ["name", "filter", "level", "message"]


def get_all_blacklists():
    return Blacklist.objects


BLACKLISTS_TABLE = {
    "object_id": "blacklist",
    "columns": [
        {"header": "Name", "lookup_key": "name"},
        {"header": "Severity", "cell_template": "geant/blacklists/_blacklist_level.html"},
        {"header": "Message", "lookup_key": "message"},
        {"header": "Actions", "cell_template": "geant/blacklists/_blacklist_actions.html"},
    ],
    "add_button": {
        "url": "geant-blacklists:new-blacklist",
        "text": "Create new blacklist",
    },
}


@require_GET
def list_blacklists(request):
    qs = get_all_blacklists().order_by("name")

    page_num = request.GET.get("page", "1")
    page = Paginator(object_list=qs, per_page=10).get_page(page_num)

    if request.htmx:
        base_template = "components/_table.html"
    else:
        base_template = "geant/blacklists/blacklist_list.html"

    context = {
        "table": BLACKLISTS_TABLE,
        "count": qs.count(),
        "page_title": "Blacklists",
        "page": page,
    }

    return render(request, base_template, context=context)


@require_http_methods(["HEAD", "GET", "POST", "DELETE"])
def edit_blacklist(request, pk=None):
    instance = None if pk is None else get_object_or_404(Blacklist, pk=pk)
    if request.method == "GET":
        context = {"form": CreateBlacklistForm(instance=instance)}
        return render(request, "geant/blacklists/blacklist_edit.html", context=context)
    elif request.method == "POST":
        form = CreateBlacklistForm(request.POST, instance=instance)
        form.save()
    elif request.method == "DELETE":
        pass
    return redirect(request, target="geant-blacklists:blacklist-list")
