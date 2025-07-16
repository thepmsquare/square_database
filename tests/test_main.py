from datetime import datetime, timedelta

from square_commons import get_api_output_in_standard_format
from square_database_structure.square.public.enums import TestEnumEnum


def test_database_creation(create_client_and_cleanup):
    pass


def test_read_main(get_patched_configuration, create_client_and_cleanup):

    client = create_client_and_cleanup
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == get_api_output_in_standard_format(
        log=get_patched_configuration.config_str_module_name
    )


# test insert_rows
def test_insert_rows(create_client_and_cleanup, fixture_insert_rows):
    client = create_client_and_cleanup
    response = client.post("/insert_rows/v0", json=fixture_insert_rows)
    assert response.status_code == 201
    response_json = response.json()
    assert "data" in response_json
    assert "main" in response_json["data"]
    assert "affected_count" in response_json["data"]
    assert len(response_json["data"]["main"]) == 1
    assert response_json["data"]["main"][0]["test_text"] == "example"
    # assert response_json["data"]["main"][0]["test_id"] == 1
    assert response_json["data"]["affected_count"] == 1
    assert "log" in response_json
    assert "message" in response_json


def test_get_rows(create_client_and_cleanup, fixture_get_rows):
    client = create_client_and_cleanup

    response = client.post(
        "/get_rows/v0",
        json=fixture_get_rows,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert "data" in response_json
    assert "main" in response_json["data"]
    assert "total_count" in response_json["data"]
    assert len(response_json["data"]["main"]) == 1
    assert response_json["data"]["main"][0]["test_text"] == "example"
    assert response_json["data"]["total_count"] == 1
    assert "log" in response_json
    assert "message" in response_json


def test_duplicate_insert_rows(
    create_client_and_cleanup, fixture_duplicate_insert_rows
):
    client = create_client_and_cleanup
    response = client.post("/insert_rows/v0", json=fixture_duplicate_insert_rows)
    assert response.status_code == 201
    response_json = response.json()
    assert "data" in response_json
    assert "main" in response_json["data"]
    assert "affected_count" in response_json["data"]
    assert len(response_json["data"]["main"]) == 1
    assert response_json["data"]["main"][0]["test_text"] == "example"
    assert response_json["data"]["affected_count"] == 1
    assert "log" in response_json
    assert "message" in response_json


def test_get_rows_with_filter(create_client_and_cleanup, fixture_get_rows_with_filter):
    client = create_client_and_cleanup

    response = client.post(
        "/get_rows/v0",
        json=fixture_get_rows_with_filter,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert "data" in response_json
    assert "main" in response_json["data"]
    assert "total_count" in response_json["data"]
    assert len(response_json["data"]["main"]) == 1
    assert response_json["data"]["main"][0]["test_text"] == "filtered_example"
    assert response_json["data"]["total_count"] == 1
    assert "log" in response_json
    assert "message" in response_json


def test_filter_by_text_eq(fixture_all_data_types):
    client = fixture_all_data_types
    response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"test_text": {"eq": "beta"}},
            "apply_filters": True,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]["main"]
    assert len(data) == 1
    assert data[0]["test_text"] == "beta"
    assert response.json()["data"]["total_count"] == 1


def test_filter_by_datetime_gt(fixture_all_data_types):
    client = fixture_all_data_types
    # Get items created after 'beta' (i.e., 'gamma', 'delta')
    filter_date = (datetime.now() - timedelta(days=7)).isoformat()
    response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"test_datetime": {"gt": filter_date}},
            "apply_filters": True,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]["main"]
    assert len(data) == 3  # beta, gamma, delta
    assert response.json()["data"]["total_count"] == 3
    assert all(item["test_text"] in ["beta", "gamma", "delta"] for item in data)


def test_filter_by_boolean_false(fixture_all_data_types):
    client = fixture_all_data_types
    response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"test_bool": {"eq": False}},
            "apply_filters": True,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]["main"]
    assert len(data) == 2  # beta, delta
    assert response.json()["data"]["total_count"] == 2
    assert all(item["test_bool"] is False for item in data)


def test_filter_by_enum_value_a(fixture_all_data_types):
    client = fixture_all_data_types
    response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"test_enum_enum": {"eq": TestEnumEnum.PENDING.value}},
            "apply_filters": True,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]["main"]
    assert len(data) == 2  # alpha, gamma
    assert response.json()["data"]["total_count"] == 2
    assert all(item["test_enum_enum"] == TestEnumEnum.PENDING.value for item in data)


def test_filter_by_float_gte(fixture_all_data_types):
    client = fixture_all_data_types
    response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"test_float": {"gte": 30.0}},
            "apply_filters": True,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]["main"]
    assert len(data) == 2  # gamma, delta
    assert response.json()["data"]["total_count"] == 2
    assert all(item["test_float"] >= 30.0 for item in data)


def test_edit_rows(create_client_and_cleanup, fixture_edit_rows):
    client = create_client_and_cleanup

    response = client.patch("/edit_rows/v0", json=fixture_edit_rows)
    assert response.status_code == 200

    response_json = response.json()
    assert "data" in response_json
    assert "affected_count" in response_json["data"]
    assert response_json["data"]["affected_count"] >= 1

    # verify edit applied
    get_response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"test_text": {"eq": "edited"}},
            "apply_filters": True,
        },
    )
    assert get_response.status_code == 200
    data = get_response.json()["data"]["main"]
    assert len(data) == 1
    assert data[0]["test_text"] == "edited"


def test_delete_rows(create_client_and_cleanup, fixture_delete_rows):
    client = create_client_and_cleanup

    response = client.post("/delete_rows/v0", json=fixture_delete_rows)
    assert response.status_code == 200

    response_json = response.json()
    assert "data" in response_json
    assert "affected_count" in response_json["data"]
    assert response_json["data"]["affected_count"] >= 1

    # verify deletion
    get_response = client.post(
        "/get_rows/v0",
        json={
            "database_name": "square",
            "schema_name": "public",
            "table_name": "test",
            "filters": {"test_text": {"eq": "to_delete"}},
            "apply_filters": True,
        },
    )
    assert get_response.status_code == 200
    data = get_response.json()["data"]["main"]
    assert len(data) == 0
