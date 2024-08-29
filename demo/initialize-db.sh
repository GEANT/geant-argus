#! /usr/bin/env bash
set -e
# purge data (delete and recreate schema, set permissions)
psql -c \
    "BEGIN; DROP SCHEMA IF EXISTS public CASCADE; \
    CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO ${PGUSER}; \
    GRANT ALL ON SCHEMA public TO public; COMMIT;"

# migrate
django-admin migrate

# initial setup: create users and groups (admin, noc, servicedesk, )
django-admin initial_setup --password admin --servicedesk-password servicedesk --noc-password noc

# populate database through create_fake_incident
django-admin create_fake_incident