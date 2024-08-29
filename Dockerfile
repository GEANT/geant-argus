# This Dockerfile is designed to run a Geant Argus for demo purposes. Together with the
# accompanying docker-compose.yaml it contains all that's needed to showcase Geant Argus.
# For additional instructions,

FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends tini \
    build-essential libpq-dev libffi-dev libssl-dev postgresql-client
RUN mkdir -p /argus

WORKDIR /argus
COPY requirements.txt /argus

RUN pip install -r requirements.txt

COPY . /argus
RUN pip install -e .

COPY ./demo /argus
RUN mv /argus/settings.py /argus/src/geant_argus/settings/demo.py

ENV PYTHONPATH=/argus/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE='geant_argus.settings.demo'

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/argus/docker-entrypoint.sh"]
