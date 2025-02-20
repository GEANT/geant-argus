import json
import os
from typing import List, Union

import pytest
import yaml
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connections
from pytest_docker.plugin import DockerComposeExecutor, execute


@pytest.fixture(scope="session")
def postgres_params():
    return {
        "database": "argus",
        "username": "bogus-user",
        "password": "bogus-password",
        "hostname": None,  # will be set later by postgres_service fixture
        "port": None,  # will be set later by postgres_service fixture
    }


@pytest.fixture(scope="session")
def postgres_compose_config(postgres_params):
    return {
        "image": "postgres:16",
        "container_name": "postgres",
        "ports": ["5432"],
        "environment": {
            "POSTGRES_USER": postgres_params["username"],
            "POSTGRES_PASSWORD": postgres_params["password"],
            "POSTGRES_DB": postgres_params["database"],  # no dashes!!
        },
        "healthcheck": {
            "test": ["CMD-SHELL", "pg_isready -U argus -d argus"],
            "interval": "2s",
            "timeout": "2s",
            "retries": 20,
        },
    }


# Pin the project name to avoid creating multiple stacks
@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    return "geant-argus-test-compose"


# Stop the stack before starting a new one
@pytest.fixture(scope="session")
def docker_setup_command():
    return ["down -v", "up --build -d"]


@pytest.fixture(scope="session")
def docker_compose_file(tmp_path_factory, postgres_compose_config):
    file = tmp_path_factory.mktemp("compose") / "docker-compose.yml"
    file.write_text(
        yaml.safe_dump(
            {
                "version": "3.8",
                "services": {
                    "postgres": postgres_compose_config,
                },
            }
        )
    )
    return str(file)


@pytest.fixture(scope="session")
def execute_docker_compose(
    docker_compose_command: str,
    docker_compose_file: Union[List[str], str],
    docker_compose_project_name: str,
):
    executor = DockerComposeExecutor(
        docker_compose_command, docker_compose_file, docker_compose_project_name
    )

    def _run_command(command):
        result = executor.execute(command)
        return result.decode()

    return _run_command


@pytest.fixture(scope="session")
def postgres_service(docker_services, execute_docker_compose, postgres_params, docker_ip):
    """Ensure that PostgreSQL is up and responsive."""

    service_name = "postgres"

    def is_healthy(c):
        result = execute(f"docker inspect {c}")
        inspect_output = json.loads(result)
        return inspect_output[0]["State"]["Health"]["Status"] == "healthy"

    # `port_for` takes a container port and returns the corresponding host port
    postgres_params["port"] = docker_services.port_for(service_name, 5432)

    # for certain setups, ip may not be 127.0.0.1
    postgres_params["hostname"] = docker_ip

    # wait until healthy
    container = execute_docker_compose(f"ps -q {service_name}")
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.5, check=lambda: is_healthy(container)
    )
    return postgres_params


@pytest.fixture(scope="session")
def django_db_modify_db_settings(uses_db_session, request):
    """This fixture is used by pytest-django (cf.
    https://pytest-django.readthedocs.io/en/latest/database.html#django-db-modify-db-settings)

    It is documented to be able to support changes to the django DATABASES setting, however, django
    caches the original state and connection, so we need to override some django internal state

    if DATABASE_URL is not set as an environment variable, we assume that the tester wants to
    spin up a postgres container and use that
    """
    if not uses_db_session:
        yield
        return

    if os.getenv("DATABASE_URL"):
        yield
        return

    postgres_service = request.getfixturevalue("postgres_service")
    new_database_setting = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": postgres_service["database"],
            "USER": postgres_service["username"],
            "PASSWORD": postgres_service["password"],
            "HOST": postgres_service["hostname"],
            "PORT": postgres_service["port"],
        },
    }

    # Now we need to update some internal django state for the database settings to be applied
    # see also https://github.com/pytest-dev/pytest-django/issues/643#issuecomment-1876257915

    prev_db_setting = settings.DATABASES

    # remove cached_property of connections.settings from the cache
    del connections.__dict__["settings"]

    # define settings to override during this fixture
    settings.DATABASES = new_database_setting

    # re-configure the settings given the changed database config
    connections._settings = connections.configure_settings(settings.DATABASES)

    # open a connection to the database with the new database config
    connections["default"] = connections.create_connection("default")

    yield

    # This step is optional since it's a session scope fixture, but it's good to be complete
    settings.DATABASES = prev_db_setting


@pytest.fixture(scope="session")
def uses_db_session(request):
    """iterates through all test functions to look for a django_db mark. If there is none, we don't
    need a database
    """
    session = request.node
    for item in session.items:
        if any(m.name == "django_db" for m in item.own_markers):
            return True
    return False


@pytest.fixture
def uses_db(request):
    return any(m.name == "django_db" for m in request.node.own_markers)


@pytest.fixture(autouse=True)
def setup_django(uses_db, request):
    if not uses_db:
        return

    # default database entries can be defined here
    request.getfixturevalue("default_user")


@pytest.fixture
def default_user():
    User = get_user_model()
    return User.objects.create_user("argus", password="password")
