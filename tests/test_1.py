from fastapi.testclient import TestClient

from square_database.configuration import config_str_module_name
from square_database.main import (
    app,
)

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "text": config_str_module_name,
    }
