#!/bin/bash
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
python3 manage.py runserver --insecure --noreload --no-color 0.0.0.0:8000
