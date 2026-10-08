from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from finance_flow.database import async_session_factory
from finance_flow.main import app
from finance_flow.models.instrument import Instrument

client = TestClient(app)


def test_create_alert_requires_authentication() -> None:
    response = client.post(
        "/api/v1/alerts",
        json={
            "instrument_id": 1,
            "direction": "above",
            "value": "42",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_alert() -> None:
    email = f"alert-api-{uuid4()}@example.com"
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
    assert "access_token" in client.cookies

    async with async_session_factory() as session:
        instrument = Instrument(
            code=f"ALERT_API_{uuid4().hex[:8]}",
            name="Alert API Test",
            type="currency",
            is_active=True,
        )
        session.add(instrument)
        await session.commit()
        await session.refresh(instrument)

        instrument_id = instrument.id

    response = client.post(
        "/api/v1/alerts",
        json={
            "instrument_id": instrument_id,
            "direction": "above",
            "value": "42.50",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["instrument_id"] == instrument_id
    assert data["direction"] == "above"
    assert Decimal(data["value"]) == Decimal("42.50")
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_alerts_returns_only_current_user_alerts() -> None:
    email = f"alert-list-api-{uuid4()}@example.com"
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
    assert "access_token" in client.cookies

    async with async_session_factory() as session:
        instrument = Instrument(
            code=f"ALERT_LIST_{uuid4().hex[:8]}",
            name="Alert List API Test",
            type="currency",
            is_active=True,
        )
        session.add(instrument)
        await session.commit()
        await session.refresh(instrument)

        instrument_id = instrument.id

    create_response = client.post(
        "/api/v1/alerts",
        json={
            "instrument_id": instrument_id,
            "direction": "below",
            "value": "35.50",
        },
    )

    assert create_response.status_code == 201

    response = client.get("/api/v1/alerts")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["instrument_id"] == instrument_id
    assert data[0]["direction"] == "below"
    assert Decimal(data[0]["value"]) == Decimal("35.50")
    assert data[0]["status"] == "active"