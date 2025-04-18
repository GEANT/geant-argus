.. _dependencies:

Dependencies
============


.. _dependencies-htmx:

htmx
----

`htmx <https://htmx.org/docs/>`_ is a client side javascript library for creating interactive web-
pages. It is based on sending asynchronous (AJAX) requests to a server to rerender parts of the
current html document on certain triggers, and swapping out just that part of the DOM. htmx is
configured through attributes on html elements. For example, consider the following html snippet::

  <button hx-post="/clicked"
      hx-trigger="click"
      hx-target="#parent-div"
      hx-swap="outerHTML">
      Click Me!
  </button>

with htmx, clicking this button will send a post request to ``/clicked``. It will then replace the
element with id ``parent-div`` with whatever (partial) html content is returned. It will swap out
the whole ``#parent-div`` element (indicated by ``hx-swap="outerHTML"``. If ``hx-swap`` was omitted
it would swap out just the inner contents of the ``#parent-div`` element. As you can see, htmx doe
not perform any html rendering itself, all it does swap out content. There are however, many ways
how htmx can swap out content. While going over the details of how htmx works is beyond the scope
of this documentation, some use cases and examples are given below.

Include form fields
###################

By default htmx will include the name and value of any form input field as to the
request, if the htmx element that triggers the request is inside a ``<form>``. This includes
``hidden`` form fields and ``<select>`` elements. You can also use the ``hx-include`` attribute
with a valid css selector to include those input values. How htmx sends the values depends on the
type of the request. If the request is a GET request it will send the values as query parameter,
otherwise the value will be sent as formdata. It is possible to send tweak which parameters
to send by setting the ``hx-params`` attribute. It is also possible to send predefined data by
setting the ``hx-vals`` attribute to a valid json map.

Override default behaviour using response headers
#################################################

The server can override the htmx client's default behaviour what to do with a reponse. This can be
done using `Response headers <https://htmx.org/docs/#response-headers>`_. You can for example set
the ``HX-Refresh`` or ``HX-Redirect`` to force the client to do a full page refresh or redirect to
a different page.

Swap out other content (out-of-band swapping)
#############################################

Sometimes you need to swap out more than one piece of html. In this case, the response must append
the additional html content to the response and set the the
`hx-swap-oob <https://htmx.org/attributes/hx-swap-oob/>`_ attribute to one of the elements on the
root element of this additional content, as well as the ``id`` of the element to swap out.


Usage in Django
###############

Argus uses the  `django-htmx <https://django-htmx.readthedocs.io/en/latest/>`_ app to support htmx
on the server side. This consists mainly of dealing with htmx request and response headers.
Whenever htmx makes a request, htmx sets the `HX-Request` request header. ``django-htmx`` reads
this header and sets the ``htmx`` attribute on the ``Request`` object. In the request views, Argus
looks for this attribute to determine whether this was a full request that should return a full
response or an htmx request that should return a partial response. Another way to use
``django-htmx`` is to use the preconfigured
`reponse classes <https://django-htmx.readthedocs.io/en/latest/http.html>`_ that automatically set
htmx response headers whenever appropriate, such as the ``HX-Redirect`` or ``HX-Refresh`` header.


.. _dependencies-hyperscript:

Hyperscript
-----------
Most of the user interaction can be achieved using htmx and the pattern of sending AJAX requests
and swapping out partial html content. However, sometimes it makes more sense to add a bit of
client-side-only interaction. For this we use `Hyperscript <https://hyperscript.org/docs/>`.
Hyperscript is developed by the same developers as htmx and is made to work alongside it. It is
a DSL that is designed to be easy to read. It reads almost as pseudo code. For example, consider
the following snippet::

  <button _="on click toggle .red on me">
  Click Me
  </button>

This button is given some hyperscript on the ``_`` attribute. When clicked, hypescript will add
the ``red`` css class on the button. If the button already has the ``red`` class, it will remove
that class. Adding or removing css classes is the most prevalent use case for hyperscript. The
added/removed classes generally associate with some css to hide or display certain elements, or
to give them specific styling. Other use cases for Hypscript in Geant Argus are removing certain
elements and to triggering or halting events.

.. _dependencies-tailwindcss:

Tailwind CSS
------------

`Tailwind CSS <https://tailwindcss.com/docs/>`_ is a "utility first" css framework, meaning that
like other css frameworks, you add classes to html elements and those classes have css definitions
associated with it that come from the framework. Most css frameworks acts as a "comoponent"
framework so you add a ``button`` class to ``<button>`` elements and these get nicely styled as a
button, or a ``card`` element to a ``<div>`` to style that element as a card. As mentioned,
Tailwind is a utiilty framework and its classes are much more low-level. For example, the class
``p-8`` adds ``padding: '2rem';`` and ``bg-white`` adds ``background-color: white``. You may say
that this looks a lot like inline css, and you're right. However, Tailwind is much more powerful
than just that. With simple modifiers such as ``sm:`` or ``lg:`` you can build behaviour responsive
to screen size. It is also possible to extend tailwind. For example, you can define a ``primary``
color based on a css variable: ``'primary': 'rgba(var(--primary))'`` and then create themes that
set this variable. In your code you would use ``bg-primary`` or ``text-primary`` and those elements
are coloured based on the current value of ``--primary``. Tailwind sits in the middle between
handcrafting your own css and having a component based framework do all the work.

Having said that, there is value in having a component based framework. This is why we also include
`Daisy UI`_. Daisy UI is a component based CSS framework built on top of tailwind, so that you `can`
add a ``btn`` class and obtain a nicely styled button, as well as many other components. It also
creates default themeable colours such as  ``primary``, ``neutral`` and ``accent``.

Now, having all these utility and component classes available, would result in a huge css file,
even when minified. A static large CSS file is also very difficult to make extensible. It is
therefore required to build your own CSS file using a command line tool that Tailwind provides:
``tailwindcss``. You point this tool to your tailwind config and a base css file that contains your
custom css definitions like so (this is an example and not the command that we use for Geant Argus,
see :ref:`compiling-tailwind-config-and-base-css`)::

  tailwindcss -c tailwind.config.js -i base.css -o final.css

In this example the ``tailwind.config.js`` contains your customizations as well as the location of
all your source (html template) files. This way ``tailwindcss`` can parse your source files and
only include the classes that you actually use. The ``base.css`` file acts as an entry point for
tailwindcss and you can include any custom css you want. The generated css file will be stored as
``final.css``. You can also build a minified version of the css file by supplying the ``-m`` flag


Installation
############

``tailwindcss`` can be automatically downloaded for your platform by running::

  make get-tailwind

This is also done as part of the ``make initialize-repo`` command. Alternatively, you can follow
the installation instructions in  `Argus documentation: Install and build Tailwind CSS and daisyUI
<https://argus-server.readthedocs.io/en/latest/reference/htmx-frontend.html#install-and-build-tailwind-css-and-daisyui>`_.
It is important to download the correct version (as specified in the ``tailwindcss/VERSION`` file).


.. _compiling-tailwind-config-and-base-css:

Compiling Tailwind config and base CSS
######################################

As described above, TailwindCSS can generate the css file from a base css file and a
``tailwind.config.js``. However, in the case of (Geant) Argus, there is no static base css file
or ``tailwind.config.js``. This is due to the fact that the sources of the two Argus projects need
to be combined. The solution to this can be found in the ``tailwind_config`` `Django management
command <https://argus-server.readthedocs.io/en/latest/customization/htmx-frontend.html#themes-and-styling>`_
supplied by Argus. This command generates the base css file and the tailwind config. For generating
the base css file, the command looks in the ``AppConfig`` of every app listed in the
``INSTALLED_APPS`` setting for a ``tailwind_css_files()`` method and creates includes in the
base.css for every file listed by that method. For Geant Argus, the css snippets are located in
the ``geant_argus/geant_argus/tailwindcss/`` directory. Snippets are ordered by name, so by
giving them a numerical value, it is possible to give certain snippets a higher priority than
others. See also `custom-css-snippets`_.

The ``tailwind.config.js`` file is generated from a template. The Django template engine is used
for this. The template location is ``tailwind/tailwind.config.js`` and the ``geant_argus`` app
has this :ref:`template overridden <overriding-templates>`. Aside from the static content in this
template, there is an important interpolated variable ``{{ projectpaths }}``. This variable is
injected with the template directory of every app in the ``INSTALLED_APPS`` setting. This way
all templates are evaluated by ``tailwindcss`` to look for tailwind classes, be they from
``argus.htmx``, ``geant_argus`` or any other app that uses tailwind.

Geant Argus has ``tailwind_config`` configured to output its results in the ``tailwindcss/``
directory as ``tailwind.config.json`` and ``geant.base.css`` for the tailwind config and the base
css respectively. The content of the files is dependent on the virtual environment in which they
were generated, so these files cannot be checked in source control. The same holds true for the
generated base css file. For Geant Argus, the only file that is checked in, is the minified
css file located in ``src/geant_argus/geant_argus/static/geant.min.css``, which is generated by
running::

  make css


.. _custom-css-snippets:

Custom CSS Snippets
###################

Custom CSS snippets are located in ``geant_argus/geant_argus/tailwindcss``. These contains the css
definitions required for certain pieces of functionality. Some of these pieces are resusable, while
others are only used for a specific part of Geant Argus.

While creating css snippets, it is possible to add tailwind directives. For example, you can use
``@apply`` to have tailwind `apply <https://tailwindcss.com/docs/functions-and-directives#apply-directive>`_
the contents of a tailwind class to a css snippet::

  .my-custom-class {
    @apply border-base-content/50 bg-base-100;
  }

.. _Daisy UI: https://daisyui.com/docs/


Upgrading dependencies
----------------------
See
`Argus Documentation: Upgrading Dependencies <https://argus-server.readthedocs.io/en/latest/development/howtos/htmx-frontend/dependencies.html>`_

