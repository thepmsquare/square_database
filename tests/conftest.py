import importlib
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def get_patched_configuration():
    def patched_join(*args):
        *rest, last = args
        if last == "config.ini":
            last = "config.testing.ini"
        elif last == "config.sample.ini":
            last = "config.testing.sample.ini"

        return original_join(*rest, last)

    original_join = os.path.join
    os.path.join = patched_join

    import square_database.configuration

    importlib.reload(square_database.configuration)
    config = square_database.configuration

    yield config

    # cleanup
    os.path.join = original_join


@pytest.fixture(scope="session")
def create_client_and_cleanup(get_patched_configuration):

    create_database_and_tables = importlib.import_module(
        get_patched_configuration.config_str_database_module_name
    ).create_database_and_tables

    create_database_and_tables(
        db_username=get_patched_configuration.config_str_db_username,
        db_port=get_patched_configuration.config_int_db_port,
        db_password=get_patched_configuration.config_str_db_password,
        db_ip=get_patched_configuration.config_str_db_ip,
    )
    from square_database.main import (
        app,
    )

    client = TestClient(app)
    yield client
    from sqlalchemy import text, create_engine

    global_list_create = importlib.import_module(
        get_patched_configuration.config_str_database_module_name
    ).main.global_list_create

    local_str_postgres_url = (
        f"postgresql://{get_patched_configuration.config_str_db_username}:{get_patched_configuration.config_str_db_password}@"
        f"{get_patched_configuration.config_str_db_ip}:{str(get_patched_configuration.config_int_db_port)}/"
    )

    postgres_engine = create_engine(local_str_postgres_url)

    with postgres_engine.connect() as postgres_connection:

        postgres_connection.execute(text("commit"))

        for database in global_list_create:

            postgres_connection.execute(
                text(f"DROP DATABASE {database['database']} WITH (FORCE)")
            )


@pytest.fixture()
def fixture_insert_rows(create_client_and_cleanup):
    client = create_client_and_cleanup
    yield {
        "database_name": "square",
        "schema_name": "public",
        "table_name": "test",
        "data": [
            {"test_text": "example"},
        ],
    }
    client.post(
        "/delete_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {},
            "apply_filters": False,
        },
    )


@pytest.fixture()
def fixture_get_rows(create_client_and_cleanup):
    client = create_client_and_cleanup
    client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": [
                {"test_text": "example"},
            ],
        },
    )
    yield {
        "database_name": "square",
        "schema_name": "public",
        "table_name": "test",
        "filters": {},
        "apply_filters": False,
    }
    client.post(
        "/delete_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {},
            "apply_filters": False,
        },
    )


@pytest.fixture()
def fixture_duplicate_insert_rows(create_client_and_cleanup):
    client = create_client_and_cleanup
    yield {
        "database_name": "square",
        "schema_name": "public",
        "table_name": "test",
        "data": [
            {"test_text": "example"},
            {"test_text": "example"},
        ],
        "skip_conflicts": True,
    }
    client.post(
        "/delete_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {},
            "apply_filters": False,
        },
    )
