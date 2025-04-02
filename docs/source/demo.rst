Dockerized Demo Instance
========================

Dockerized demo instance as the simplest way to run Geant Argus::

  docker compose up -d

log in using admin//admin
curated incidents in ``demo/incidents/`` directory

Reinitialization of existing volume either set the ``FORCE_INITIALIZE=1`` (do not commit this change), or run::

  docker compose exec -t argus ./initialize-db.py --force