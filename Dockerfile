# This Dockerfile is designed to run a Geant Argus for demo purposes. Together with the
# accompanying docker-compose.yaml it contains all that's needed to showcase Geant Argus.
# For additional instructions,

FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends tini \
    build-essential libpq-dev libffi-dev libssl-dev
RUN mkdir -p /argus
COPY . /argus


WORKDIR /argus
RUN pip install -r requirements.txt && pip install -e .

ENV PYTHONPATH=/argus/src
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["/usr/bin/tini", "-v", "--"]
CMD ["/argus/docker-entrypoint.sh"]
