#! /usr/bin/env bash

# purge data (delete and recreate schema, set permissions)
psql -h ${POSTGRES_HOST} -U argus -d argus

# migrate

# initial setup: create users and groups (admin, noc, servicedesk, )
django-admin initial_setup

# populate database through create_fake_incident