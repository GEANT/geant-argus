.. _confguration:

Configuration
=============

Django reads all settings from a ``settings`` file. The Geant Argus settings
files are on in the directory  ``src/geant_argus/settings``. There are three ``settings`` files
available:

* ``base.py`` contains settings that are used for all Geant Argus instances
* ``dev.py`` contains settings that are only used during development. For example, here we set
  ``DEBUG=True``
* ``prod.py`` contains settings that are only used in deployed instances of argus, ie test, uat
  and production

Then there are also settings coming directly from Argus:

* ``argus.site.settings.base``: most base Argus settings
* ``argus.site.settings.backend``: settings that are relevant for deployed instances of Argus

For a good number of settings it is perfectly fine to provide a static value in one of the
``settings`` files. However, some settings need to be provided as environment variables. These
include settings that differ between test, uat and production, but also include secrets. In the
various settings files, these are read from the environment using ``get_str_env`` or
``get_bool_env``.


.. _custom-cmd-sh-files:

Custom ``cmd.sh`` files
------------------------

Some of the environment based settings are also needed during development, and thus need to be
set. While it is possible to set them manually or create a ``.env`` file and use ``source .env``,
it is often easier to place them in a ``.sh`` script together with an invocation of ``manage.py``
(the canonical way to start Django commands, see also :ref:`management-commands`). This way you can
set up multiple ``cmd.sh`` files that can for example point to different databases: a local
database and the one running in the test environment. A ``cmd.sh-template`` file exists in the
repository root to provide default values.

See also `Argus documentation: Applying settings and switching between them
<https://argus-server.readthedocs.io/en/latest/development/notes.html#applying-settings-and-switching-between-them>`_.


.. _config-json::

Config JSON file
----------------

Another where settings may reside is in a ``config.json`` file. A special environment variable
``CONFIG_FILENAME`` can be set that points to a json file containing settings. These settings
may be environment dependent. This contents of this file must be a json object. Any key in this
object is set as an attribute of the ``django.conf.settings`` object. Keys are therefore generally
UPPER_CASE. The main use case for this is to supply settings that are not a single value, such
as a list or a nested dict, and that vary between environments, so they cannot be supplied as
static values.


.. _settings-overview:

Settings overview
-----------------

Below are some of the important settings explained

* ``INSTALLED_APPS``: A list of Django apps that Django will initialize when starting up
* ``ROOT_URLCONF``: The main entry point for Django url routing. All url patterns must be defined,
  imported or included in this module
* ``INCIDENT_TABLE_COLUMNS``: The list of all columns to show in the incident list
* ``STATUS_CHECKER_ENABLED``, ``STATUS_CHECKER_HEALTH_URL``, ``STATUS_CHECKER_INPROV_URL``:
  settings related to the status checker in the top right of the Geant Argus incident list page
* ``TTS_URL_BASE``: The Otobo ticket ref base url. Used to reconstruct the ticket url when a user
  updates the ticket ref
* ``NEW_INCIDENT_AURAL_ALERTS`` and ``NEW_INCIDENT_AURAL_ALERT_DEFAULT``: The available sounds for
  the :ref:`preferences-aural-alert` preference.
* ``ACK_REMINDER_MINUTES`` and ``ACK_REMINDER_MINUTES_DEFAULT``: The time delay settings for
  the :ref:`preferences-ack-reminder` preference.

See also `Argus documentation: Site-specific settings
<https://argus-server.readthedocs.io/en/latest/reference/site-specific-settings.html>`_ for more
Argus settings

