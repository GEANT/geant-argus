import json
import os
from typing import List, Union
import dj_database_url
import pytest
from pytest_docker.plugin import DockerComposeExecutor, execute
import yaml


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


@pytest.fixture
def setup_db(request, settings):
    """if DATABASE_URL is not set as an environment variable, assume that the tester wants to
    spin up a postgres container and use that
    """
    if not (DATABASE_URL := os.getenv("DATABASE_URL")):
        postgres_service = request.getfixturevalue("postgres_service")
        DATABASE_URL = "postgresql://{username}:{password}@{hostname}:{port}/{database}".format(
            **postgres_service
        )
    settings.DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL),
    }
    settings


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    # result = any(m.name == "django_db" for m in request.node.own_markers)
    ...


@pytest.fixture
def uses_db(request):
    result = any(m.name == "django_db" for m in request.node.own_markers)
    if result:
        request.getfixturevalue("setup_db")  # postgres is setup
        request.getfixturevalue("db")  # ensure db is loaded
    return result


@pytest.fixture(autouse=True)
def setup_django(uses_db):
    if not uses_db:
        return
