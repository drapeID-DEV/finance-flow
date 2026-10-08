from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from finance_flow.database import async_session_factory
from finance_flow.main import app
from finance_flow.models.user import User

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


def test_update_instrument_status_requires_admin() -> None:
    email = f"user-status-{uuid4()}@example.com"
    password = "test-password-123"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.patch(
        "/api/v1/instruments/USD/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_can_update_instrument_status() -> None:
    email = f"admin-status-{uuid4()}@example.com"
    password = "test-password-123"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    async with async_session_factory() as session:
        user_result = await session.execute(
            select(User).where(User.email == email)
        )
        user = user_result.scalar_one()

        user.role = "admin"
        await session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.patch(
        "/api/v1/instruments/USD/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == "USD"
    assert data["is_active"] is False

    restore_response = client.patch(
        "/api/v1/instruments/USD/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "is_active": True,
        },
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_admin_update_unknown_instrument() -> None:
    email = f"admin-unknown-{uuid4()}@example.com"
    password = "test-password-123"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one()
        user.role = "admin"
        await session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.patch(
        "/api/v1/instruments/UNKNOWN/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Instrument not found"