from fastapi.testclient import TestClient

from finance_flow.main import app

client = TestClient(app)


def test_application_starts() -> None:
    response = client.get("/docs")

    assert response.status_code == 200