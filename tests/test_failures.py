from fastapi import status

from square_database.messages import messages


def test_insert_rows_invalid_database(create_client_and_cleanup):
    """Test inserting rows with an invalid database name"""
    client = create_client_and_cleanup
    response = client.post(
        "/insert_rows/v0",
        json={
            "database_name": "invalid_db",
            "schema_name": "public",
            "table_name": "test",
            "data": [{"test_text": "example"}],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["INCORRECT_DATABASE_NAME"] in response.json()["message"]


def test_insert_rows_invalid_schema(create_client_and_cleanup):
    """Test inserting rows with an invalid schema name"""
    client = create_client_and_cleanup
    response = client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "invalid_schema",
            "table_name": "test",
            "data": [{"test_text": "example"}],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["INCORRECT_SCHEMA_NAME"] in response.json()["message"]


def test_insert_rows_invalid_table(create_client_and_cleanup):
    """Test inserting rows with an invalid table name"""
    client = create_client_and_cleanup
    response = client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "invalid_table",
            "data": [{"test_text": "example"}],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["INCORRECT_TABLE_NAME"] in response.json()["message"]


def test_insert_rows_invalid_data(create_client_and_cleanup):
    """Test inserting rows with invalid data structure"""
    client = create_client_and_cleanup
    response = client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": [{"invalid_column": "example"}],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["GENERIC_400"] in response.json()["message"]


def test_get_rows_invalid_filter(create_client_and_cleanup):
    """Test getting rows with invalid filter condition"""
    client = create_client_and_cleanup
    response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"invalid_column": {"eq": "value"}},
            "apply_filters": True,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["GENERIC_400"] in response.json()["message"]


def test_get_rows_invalid_order_by(create_client_and_cleanup):
    """Test getting rows with invalid order_by column"""
    client = create_client_and_cleanup
    response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "order_by": ["invalid_column"],
            "filters": {},
            "apply_filters": False,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["GENERIC_400"] in response.json()["message"]


def test_edit_rows_invalid_data(create_client_and_cleanup, fixture_edit_rows):
    """Test editing rows with invalid data structure"""
    client = create_client_and_cleanup
    # First insert a row to edit
    client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": [{"test_text": "to_edit"}],
        },
    )

    # Try to edit with invalid data
    response = client.patch(
        "/edit_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"test_text": {"eq": "to_edit"}},
            "data": {"invalid_column": "new_value"},
            "apply_filters": True,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["GENERIC_400"] in response.json()["message"]


def test_edit_rows_invalid_filter_column(create_client_and_cleanup):
    """Test editing rows with invalid filter column"""
    client = create_client_and_cleanup
    response = client.patch(
        "/edit_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"invalid_column": {"eq": "value"}},
            "data": {"test_text": "new_value"},
            "apply_filters": True,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["GENERIC_400"] in response.json()["message"]


def test_delete_rows_invalid_filter_column(create_client_and_cleanup):
    """Test deleting rows with invalid filter column"""
    client = create_client_and_cleanup
    response = client.post(
        "/delete_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"invalid_column": {"eq": "value"}},
            "apply_filters": True,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["GENERIC_400"] in response.json()["message"]


def test_invalid_enum_value(create_client_and_cleanup):
    """Test inserting an invalid enum value"""
    client = create_client_and_cleanup
    response = client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": [{"test_text": "example", "test_enum_enum": "INVALID_VALUE"}],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["GENERIC_400"] in response.json()["message"]


def test_invalid_column_insert(create_client_and_cleanup):
    """Test inserting rows with an invalid column name"""
    client = create_client_and_cleanup
    response = client.post(
        "/insert_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "data": [{"invalid_column": "example"}],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages["GENERIC_400"] in response.json()["message"]
