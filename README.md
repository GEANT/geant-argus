# Geant Argus
Geant specific customizations for [Argus](https://github.com/Uninett/Argus/) and
[argus-htmx-frontend](https://github.com/Uninett/argus-htmx-frontend/) for use of Argus in the
Geant NOC

Argus is an existing incident aggregator and -dashboard application developed by
Sikt/Uninett/Norgenet. As of 2024, it is envisioned to replace the current Geant dashboard alarms
frontend for the NOC. Argus is an application written in Django. This web framework has excellent
extension/customization capabilities, which makes it relatively easy to slightly modify
applications written in Django

## Development


### Installation

Install this package editable

```python
pip install -e[dev]
```

alternatively you can also install [Argus](https://github.com/Uninett/Argus/) and
[argus-htmx-frontend](https://github.com/Uninett/argus-htmx-frontend/) editable by first checking
out those repos

### Create a cmd.sh
To help with setting the correct environment variables, you can create a `cmd.sh` from the
`cmd.sh-template`.
```bash
cp cmd.sh-template cmd.sh
chmod +x cmd.sh
```
Then fill in the required environment variables such as `SECRET_KEY` and `DATABASE_URL`.
You can then call Django management commands through this cmd (eg. `./cmd.sh runserver`)
*Note* obtaining a running Postgres server is not part of this Readme

### Tailwind
This project uses Tailwind together with Daisy UI for css styling. It is recommended to use the
[standalone CLI](https://tailwindcss.com/blog/standalone-cli). In that case make sure to use a
version that [includes Daisy](https://github.com/dobicinaitis/tailwind-cli-extra). Download the
version for your platform from [Github](https://github.com/dobicinaitis/tailwind-cli-extra/releases),
and put it somewhere on your path (eg `/usr/local/bin`).

You then need to generate a `tailwind.config.js` that points to the installed dependencies and
build the tailwind css:

```
./cmd.sh tailwind_config
tailwindcss -i src/geant_argus/geant_argus//static/themes/.geant.css -o src/geant_argus/geant_argus//static/themes/geant.css
```
To have `tailwindcss` automatically pick up changes, run that command with the `-w` watch flag.

### Prepare database for first use
If you connected to a virgin postgres database, you first need to prepare it

```
./cmd.sh migrate
./cmd.sh createsuperuser
./cmd.sh initial_setup
```

###
You can now run the development server
```
./cmd.sh runserver
```

## Customization techniques
In order to customize Argus, we a number of techniques. These are described below. Some of this
information can also be found [here](https://argus-server.readthedocs.io/en/latest/site-specific-settings.html)

*note*: A Django application is organized into Apps (see below). In order to prevent confusion, in
this write-up, a full Django application is referred to as a Site, and the individual apps as Apps.


### Settings
Every Django Site is goverened by a `settings` file that contains the settings for running a
particular instance of a Site. Settings may import other settings files. For `geant-argus` we have
settings files located in the `src/geant_argus/settings`. We have settings for `dev` and `prod` for
running geant-argus in either development or deployed environments (test/uat/prod all make use of
the `prod.py` settings. Settings tied to a specific deployed environment are managed using puppet).
There is also the `base.py` settings file which contains settings that are valid for all instances
of geant-argus. This file includes `argus.site.settings.base` as the base Argus settings.


### Extra apps
Django has the concept of Apps. An app is a collection of code and/or data models and a Django
site is a collection of one of more Apps. Which Apps are loaded is indicated in the
`INSTALLED_APPS` setting. For Geant Argus we have the following additional apps
* `geant_argus` an app containing our all our customizations
* `argus_site` a references to the `argus.site` package as an app (required for some template
    overriding)
* `django_htmx` the generic package that implements htmx for a django Site
* `argus_htmx` the (new) Argus front-end using htmx

Some of our extra Apps are appended to the default `INSTALLED_APPS` setting, while others are
prepended. When resolving a certain resource, such as a template, Django traverses the installed
Apps in forward direction and returns the first resource that matches its name. This means that
prepended Apps can override existing resources, while appended Apps cannot.

See also: [https://docs.djangoproject.com/en/5.0/ref/applications/](https://docs.djangoproject.com/en/5.0/ref/applications/s)


### Templates
Like many web frameworks, Django uses templates for rendering (html) pages. Templates are
identified by a their relative path in valid `templates/` directories. Because every App can have
their own `templates/` directory, it is possible to override an existing template by creating a
new file with the same name in another App `templates/` directory. We use this for example for
implementation of the incidents details page `htmx/incidents/incident_detail.html` which overrides
a template from the `argus_htmx` App.

*note* Argus has a default setting `TEMPLATES[0]["DIRS"]` that disables Django's behaviour of
resolving templates in the apps' directories. We reset this setting in our `base.py` settings file

*note* by reverting this setting, Django can by default no longer resolve the templates in the
`argus.site` package, since this is not marked as a Djanog App. We mark this as a Django app by
creating our own custom `AppConfig` class that refers to this package (see
`geant_argus.argus_site.apps.py`) so that `argus.site` templates are resolved.

See also: [https://docs.djangoproject.com/en/5.0/howto/overriding-templates/](https://docs.djangoproject.com/en/5.0/howto/overriding-templates/)


#### Template tags
While not necessarily a customization of existing Argus behaviour, it is useful to mention template
tags. Template tags (and filters) are the mechanism with which to extend Django's templating
functionality. We currently don't implement our own template tags, but do have some template
filters. Djanog does not allow arbitrary expressions when rendering templates. Instead, if you want
to modify a value passed into a template, you need to use a filter. Filters can
be defined in python module inside an App's `templatetags/` directory:

```
# myfilters.py
from django import template
register = template.Library()

@register.filter
def my_filter(arg1, arg2):
    ...
```

`my_filter` can then be used inside a Django template as following:
```
{% load myfilters %}
{{ my_value|my_filter:some_argument }}
```

The filter must first be loaded through the `{% load myfilters %}` directive. This searches
every installed app for a `myfilters.py` in its `templatetags` directory and loads that file. The
subsequent template interpolation call invokes `my_filter` with `my_value` as its first argument
and `some_argument` as its second argument. Filters can have one or two arguments. For filters that
have only one argument you can omit the `:...` when invoking the filter. The return value of the
filter is used when rendering the template.

See also: [https://docs.djangoproject.com/en/5.0/howto/custom-template-tags/](https://docs.djangoproject.com/en/5.0/howto/custom-template-tags/)


#### Context processors
Another useful way to add some functionality is the concept of context processors. When rendering a
template in a Django view, you must supply a context that contains all the variables that you need
to access in your template. Some variables are tied to that specific view, but sometimes you want
to add a variable into every view of the Site, such as the current logged in user, or another
global variable. In that case it is useful to use a context processor. These are functions that,
when registered, are called every time a template is rendered. They take in the current `request`
as a single argument and must return a dictionary. This dictionary is then merged with the current
context and eventually passed to the target template. A context processor function can
be activated by adding a reference to it to the `TEMPLATES[0]["OPTIONS"]["context_processors"]`
setting. An example of a context processor we use is the `geant_argus.context_processors.geant_theme`
context processor, which inject a `theme` variable (see also Theme below)

See also: [https://docs.djangoproject.com/en/5.0/ref/templates/api/#writing-your-own-context-processors](https://docs.djangoproject.com/en/5.0/ref/templates/api/#writing-your-own-context-processors)


### Urls
Additional url endpoints (views) can be added to the `url_patterns` variable in `geant_argus.urls`.
That module is assigned to the `ROOT_URLFCONF` setting and extends the default `argus.site.urls`
urls.


### Middleware
Django has the concept of middleware. These are functions or classes that can add behaviour to
every request made in the Site. They take in the current `Request` and a `get_response` function
and must return a `Response`, usually the result of the `get_response` function. They can also
terminate early by returning a custom `Response` (for example a `401 Unauthorized` for
authentication middleware) The `get_response` function calls the next middleware in the chain
(middleware can be stacked!) or the view itself.

We currently have added middleware to validate incident metadata (although this may be changed in
the future in case Argus exposes a hook for validating incident metadata directly)

See also: [https://docs.djangoproject.com/en/5.0/topics/http/middleware/](https://docs.djangoproject.com/en/5.0/topics/http/middleware/)


### Migrations
A way to update the data model is to add database migrations. These can add new resources models
(tables) to the database or update existing ones. It is not recommended to add or modify columns
to existing tables, since the code using that model is most likely not goverened by us and
therefore unaware of the changes we made, but it is possible to make small tweaks to a table, such
as adding an index. Migrations can depend on other migrations in the same app but also on
migrations in a different app. See `geant_argus.migrations.0002_incident_metadata_description_gin_idx.py`
for an example.


### Theme
`argus_htmx` supports basic theming. Theming involves setting a `theme` variable in the template
rendering context refering to a `{theme}.css` file in the `static/themes/`  directory. This css
is then included in every page. We currently have one theme: `geant.css` that contains all our css
customizations


### Incident overview table columns
The incident listing table has a default set of columns. For geant-argus we want to customize
these columns to show information that is relevant to Geant for every incident. This can be done
by overriding or extending the `INCIDENT_TABLE_COLUMNS` setting. See also
`argus_htmx.settings.INCIDENT_TABLE_COLUMNS`


### Filter backend
For geant-argus we implement custom incident filtering capabilities. We need to be able to filter
by custom boolean rules (combination of AND and OR filters) and we provide this functionality
through a filtering backend plugin. The api of this plugin is in its early stages, but currently
involves pointing Argus to a module containing the relevant objects through the
`ARGUS_FILTER_BACKEND` settings. See also `argus.filter.default` for which objects to expose and
their default implementation
