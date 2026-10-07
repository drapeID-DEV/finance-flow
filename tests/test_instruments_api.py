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


def test_get_instrument_rate_history() -> None:
    response = client.get(
        "/api/v1/instruments/USD/rates"
        "?from=2026-10-01&to=2026-10-02"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    rate = data[-1]

    assert rate["date"] == "2026-10-02"
    assert rate["unit"] == 1

def test_get_instrument_volatility() -> None:
    response = client.get(
        "/api/v1/instruments/USD/volatility"
        "?from=2026-10-01&to=2026-10-02"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == "USD"
    assert data["from"] == "2026-10-01"
    assert data["to"] == "2026-10-02"
    assert "volatility" in data

def test_compare_instruments() -> None:
    response = client.get(
        "/api/v1/instruments/compare"
        "?first=USD&second=EUR&from=2026-10-01&to=2026-10-02"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    item = data[0]

    assert "date" in item
    assert "first_rate" in item
    assert "second_rate" in item

def test_get_significant_changes() -> None:
    response = client.get(
        "/api/v1/instruments/USD/significant-changes"
        "?from=2026-10-01&to=2026-10-02&threshold=0.01"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        item = data[0]

        assert "date" in item
        assert "rate" in item
        assert "change" in item