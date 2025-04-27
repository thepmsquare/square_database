from square_commons import get_api_output_in_standard_format


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
    # assert response_json["data"]["main"][0]["test_id"] == 1
    assert response_json["data"]["total_count"] == 1
    assert "log" in response_json
    assert "message" in response_json
