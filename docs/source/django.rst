Django concepts
===============

In general, explaining Django internals is out of scope for this documentation. However, for
some concepts it is useful to at least briefly provide some information. Whenever Django (ie
Django's :django:`WSGI <howto/deployment/wsgi/>` entrypoint) receives
a request. The following happens:

* The request is routed using :ref:`urlpatterns` to a view (function)
* Before being given to the view, the request is passed through various :ref:`middleware`
* The view processes the request and builds a reponse, often using :ref:`templates`
* The response is passed through the Middleware in reverse order before being sent out

.. _urlpatterns:

URL Patterns
------------

When the request is first accepted, it is routed to a View or view function. This is done through
``urlpatterns`` defined in various ``urls.py`` files. The root URL Patterns file is defined in the
``ROOT_URLCONF`` setting. This file contains a ``urlpatterns`` attribute that has a list of
``path``\s. Paths define a url prefix and a target. A target may be a view function, or may further
dispatch a request to another ``urls`` module, in which case the path's url prefix is stripped
from the url. In case the target is a view function, that function will be called to generate a
response. But first the configured Middleware are called.

See also: :django:`Django Documentation: URL dispatcher<topics/http/urls/>`

.. _middleware:

Middleware
----------
Middleware are functions or classes that receive a http request, can pre-process that request and
pass it through to the next Middleware, and eventually the View. Common use cases for middleware
are:

* Authentication
* Session managment
* Other security aspects, such as CSRF protection

Which Middleware is active is configured using the ``MIDDLEWARE`` setting. See also
:django:`Django Documentation: Middleware <ref/middleware/>`


.. _templates:

Templates
---------

When responding to a HTTP request in Django, you often send the result of a rendered template as a
response. In the view function

See also: :argus:`Argus Documentation: Override Templates
<development/howtos/htmx-frontend/override_templates.html#override-templates>`

.. _management-commands:

Management commands
-------------------

django admin vs manage.py, DJANGO_SETTINGS_MODULE. various builtin management commands