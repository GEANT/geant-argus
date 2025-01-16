from urllib.parse import urlencode

from django import shortcuts
from django.http import HttpRequest
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh
from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def refresh(request: HtmxHttpRequest, target):
    redirect_to = reverse(target)
    if request.htmx:
        return HttpResponseClientRefresh()
    return shortcuts.redirect(redirect_to)


def redirect(request: HtmxHttpRequest, target, params=None):
    redirect_to = reverse(target)
    if params:
        redirect_to += "?" + urlencode(params, doseq=True)
    if request.htmx:
        return HttpResponseClientRedirect(redirect_to)
    return shortcuts.redirect(redirect_to)
