from django.http import HttpRequest
from django import shortcuts
from django.urls import reverse
from django_htmx.http import HttpResponseClientRefresh, HttpResponseClientRedirect
from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def refresh(request: HtmxHttpRequest, target):
    redirect_to = reverse(target)
    if request.htmx:
        return HttpResponseClientRefresh()
    return shortcuts.redirect(redirect_to)


def redirect(request: HtmxHttpRequest, target):
    redirect_to = reverse(target)
    if request.htmx:
        return HttpResponseClientRedirect(redirect_to)
    return shortcuts.redirect(redirect_to)
