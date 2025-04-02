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


.. _settings-overview:

Settings overview
-----------------

Below are some of the important settings explained

See also `Argus documentation: Site-specific settings
<https://argus-server.readthedocs.io/en/latest/reference/site-specific-settings.html>`_.

