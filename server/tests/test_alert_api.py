from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.instrument import Instrument


@pytest.mark.asyncio
async def test_create_alert_requires_authentication(client: AsyncClient) -> None:
    response = await client.post("/api/v1/alerts", json={
        "instrument_id": 1, "direction": "above", "value": "42"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_alert(client: AsyncClient, db_session: AsyncSession) -> None:
    email, password = f"alert-api-{uuid4()}@example.com", "test-password-123"
    register = await client.post("/api/v1/auth/register", json={
        "email": email, "password": password
    })
    assert register.status_code == 201
    login = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password
    })
    assert login.status_code == 200
    assert "access_token" in client.cookies

    instrument = Instrument(
        code=f"ALERT_API_{uuid4().hex[:8]}", name="Alert API Test",
        type="currency", is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()
    await db_session.refresh(instrument)

    response = await client.post("/api/v1/alerts", json={
        "instrument_id": instrument.id, "direction": "above", "value": "42.50"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["instrument_id"] == instrument.id
    assert data["direction"] == "above"
    assert Decimal(data["value"]) == Decimal("42.50")
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_alerts_returns_only_current_user_alerts(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email, password = f"alert-list-api-{uuid4()}@example.com", "test-password-123"
    register = await client.post("/api/v1/auth/register", json={
        "email": email, "password": password
    })
    assert register.status_code == 201
    login = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password
    })
    assert login.status_code == 200
    assert "access_token" in client.cookies

    instrument = Instrument(
        code=f"ALERT_LIST_{uuid4().hex[:8]}", name="Alert List API Test",
        type="currency", is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()
    await db_session.refresh(instrument)

    created = await client.post("/api/v1/alerts", json={
        "instrument_id": instrument.id, "direction": "below", "value": "35.50"
    })
    assert created.status_code == 201

    response = await client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["instrument_id"] == instrument.id
    assert data[0]["direction"] == "below"
    assert Decimal(data[0]["value"]) == Decimal("35.50")
    assert data[0]["status"] == "active"



@pytest.mark.asyncio
async def test_update_alert(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    email = f"alert-update-{uuid4()}@example.com"
    password = "test-password-123"

    register = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200

    instrument = Instrument(
        code=f"ALERT_EDIT_{uuid4().hex[:8]}",
        name="Alert Edit Test",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    created = await client.post(
        "/api/v1/alerts",
        json={
            "instrument_id": instrument.id,
            "direction": "above",
            "value": "42",
        },
    )
    assert created.status_code == 201

    alert_id = created.json()["id"]

    response = await client.patch(
        f"/api/v1/alerts/{alert_id}",
        json={"direction": "below", "value": "40"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alert_id
    assert data["direction"] == "below"
    assert Decimal(data["value"]) == Decimal("40")
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_update_alert_rejects_duplicate(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    email = f"alert-duplicate-{uuid4()}@example.com"
    password = "test-password-123"

    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200

    instrument = Instrument(
        code=f"ALERT_DUP_{uuid4().hex[:8]}",
        name="Alert Duplicate Test",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    first = await client.post(
        "/api/v1/alerts",
        json={
            "instrument_id": instrument.id,
            "direction": "above",
            "value": "42",
        },
    )
    second = await client.post(
        "/api/v1/alerts",
        json={
            "instrument_id": instrument.id,
            "direction": "below",
            "value": "40",
        },
    )
    assert first.status_code == 201
    assert second.status_code == 201

    response = await client.patch(
        f"/api/v1/alerts/{second.json()['id']}",
        json={"direction": "above", "value": "42"},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_alert_cannot_modify_another_users_alert(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    password = "test-password-123"

    first_email = f"alert-owner-{uuid4()}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": first_email, "password": password},
    )
    await client.post(
        "/api/v1/auth/login",
        json={"email": first_email, "password": password},
    )

    instrument = Instrument(
        code=f"ALERT_OWNER_{uuid4().hex[:8]}",
        name="Alert Owner Test",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    created = await client.post(
        "/api/v1/alerts",
        json={
            "instrument_id": instrument.id,
            "direction": "above",
            "value": "42",
        },
    )
    assert created.status_code == 201
    alert_id = created.json()["id"]

    await client.post("/api/v1/auth/logout")

    second_email = f"alert-other-{uuid4()}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": second_email, "password": password},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": second_email, "password": password},
    )
    assert login.status_code == 200

    response = await client.patch(
        f"/api/v1/alerts/{alert_id}",
        json={"direction": "below", "value": "40"},
    )

    assert response.status_code == 404
