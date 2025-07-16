import importlib
import os
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from square_database_structure.square.public.enums import TestEnumEnum


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
        drop_if_exists=True,
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


@pytest.fixture()
def fixture_get_rows_with_filter(create_client_and_cleanup):
    client = create_client_and_cleanup
    client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": [
                {"test_text": "filtered_example"},
                {"test_text": "another_example"},
            ],
        },
    )
    yield {
        "database_name": "square",
        "schema_name": "public",
        "table_name": "test",
        "filters": {"test_text": {"eq": "filtered_example"}},
        "apply_filters": True,
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
def fixture_all_data_types(create_client_and_cleanup):
    client = create_client_and_cleanup

    now = datetime.now()
    data_to_insert = [
        {
            "test_text": "alpha",
            "test_datetime": (now - timedelta(days=10)).isoformat(),
            "test_bool": True,
            "test_enum_enum": TestEnumEnum.PENDING.value,
            "test_float": 10.5,
            "test_json": {"key": "value_1", "id": 1},
        },
        {
            "test_text": "beta",
            "test_datetime": (now - timedelta(days=5)).isoformat(),
            "test_bool": False,
            "test_enum_enum": TestEnumEnum.PENDING.value,
            "test_float": 20.0,
            "test_json": {"key": "value_2", "id": 2},
        },
        {
            "test_text": "gamma",
            "test_datetime": now.isoformat(),
            "test_bool": True,
            "test_enum_enum": TestEnumEnum.COMPLETED.value,
            "test_float": 30.1,
            "test_json": {"key": "value_3", "id": 3},
        },
        {
            "test_text": "delta",
            "test_datetime": (now + timedelta(days=5)).isoformat(),
            "test_bool": False,
            "test_enum_enum": TestEnumEnum.RUNNING.value,
            "test_float": 40.99,
            "test_json": {"key": "value_4", "id": 4},
        },
    ]

    client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": data_to_insert,
        },
    )
    yield client

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
def fixture_edit_rows(create_client_and_cleanup):
    client = create_client_and_cleanup

    # insert a row to edit
    client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": [{"test_text": "to_edit"}],
        },
    )

    yield {
        "database_name": "square",
        "schema_name": "public",
        "table_name": "test",
        "filters": {"test_text": {"eq": "to_edit"}},
        "data": {"test_text": "edited"},
        "apply_filters": True,
    }

    # cleanup
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
def fixture_delete_rows(create_client_and_cleanup):
    client = create_client_and_cleanup
    # insert a row to delete
    client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": [{"test_text": "to_delete"}],
        },
    )
    yield {
        "database_name": "square",
        "schema_name": "public",
        "table_name": "test",
        "filters": {"test_text": {"eq": "to_delete"}},
        "apply_filters": True,
    }
    # cleanup
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
