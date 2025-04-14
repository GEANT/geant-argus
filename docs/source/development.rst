Development Guide
==================

Initial setup
-------------

After checking out the repository, a number of steps need to be taken to prepare your checkout for
development.


Install the package
####################

You will probably first want to create a virtual environment using your favorite venv tool. On
MacOS you may need to escape the brackets using `\`::

  pip install -e .[dev]


Setup pre-commit
#################

`Pre-commit <https://pre-commit.com/>`_ is a tool that can install itself as a git commit hook::

  pip install pre-commit
  pre-commit install

Every time you want to commit, certain scripts are run to check your commit. The hooks that are run
can be found in ``.pre-commit-config.yaml``.


Initialize local repository files
#################################
Now there are some local files to create. You need a :ref:`custom cmd.sh file <custom-cmd-sh-files>`
and the tailwind css files. To build the tailwind css files, you also need the ``tailwindcss`` cli
tool, see :ref:`dependencies-tailwindcss` and `Argus documentation: Install and build Tailwind CSS and daisyUI
<https://argus-server.readthedocs.io/en/latest/reference/htmx-frontend.html#install-and-build-tailwind-css-and-daisyui>`_

These can all be downloaded and/or created for you by running::

  make initialize-repo


Update ``cmd.sh``
#################

After creation, you may want to update the following environment variables in ``cmd.sh``

* ``DATABASE_URL`` to point to a different database, eg the test database. See `Argus documentation:
  Database settings <https://argus-server.readthedocs.io/en/latest/reference/site-specific-settings.html#database-settings>`_
* ``ARGUS_DASHBOARD_ALARMS_DISABLE_SYNCHRONIZATION=0`` in case you connect to the test database.
  See :ref:`back-synchronization`
* Any variable that begins with ``ARGUS_OIDC_`` to setup :ref:`single-sign-on`

For the rest of this initial setup, it is assumed that you keep the default ``cmd.sh`` values,
which means you need to setup a PostgreSQL database running on ``localhost:5432``. Luckily this
is easy to do using the provided docker compose file, which will create a postgres container
running a database that Argus can connect to::

  docker compose -f postgres-compose.yml up -d


Setting up thte database
########################

You can now initialize the database::

  ./cmd.sh migrate

To create initial data in the database, run the following commands (run
``./cmd.sh initial_setup --help`` for an overview of the different flags for this command)::

  ./cmd.sh initial_setup
  ./cmd.sh create_fake_incident --metadata-file metadata.sample.json


Run the development server
##########################

Finally, run the Django development server::

  ./cmd.sh runserver

You can log in using the credentials generated in the previous step when running ``initial_setup``


Important commands
------------------

When developing, it is recommended to have ``tailwindcss`` watch your source directory and
recompile the (development) css file whenever changes are detected. The command for this is in the
Makefile::

  make watch-tailwind

However, this command cannot detect changes to the ``tailwind.config.js`` template in
``src/geant_argus/geant_argus/templates/tailwind/`` or any newly created snippets in
``src/geant_argus/geant_argus/tailwindcss/``. If you make any changes to these, it may be necessary
to restart the ``watch-tailwind`` command.


Testing
-------

Testing requires PostgreSQL which runs in Docker. When running the tests, either through ``tox``
or by invoking ``pytest`` directly, a PostgreSQL container is started using Docker compose. If you
don't have docker installed, the tests will fail.