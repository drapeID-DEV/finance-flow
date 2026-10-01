from fastapi.testclient import TestClient

from finance_flow.main import app


client = TestClient(app)


def test_get_instruments() -> None:
    response = client.get("/api/v1/instruments")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

def test_get_instruments_with_page() -> None:
    response = client.get("/api/v1/instruments?page=1")

    assert response.status_code == 200
    assert isinstance(response.json(), list)