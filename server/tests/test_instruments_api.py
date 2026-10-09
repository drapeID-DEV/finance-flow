from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.instrument import Instrument
from finance_flow.models.rate import Rate
from finance_flow.models.user import User


async def add_instrument_with_rates(
    db_session: AsyncSession,
    code: str,
    name: str,
    rates: dict[date, Decimal] | None = None,
) -> Instrument:
    # Reuse instruments that may already exist in finance_flow_test from
    # earlier runs. Test setup must not depend on an empty database.
    result = await db_session.execute(
        select(Instrument).where(Instrument.code == code)
    )
    instrument = result.scalar_one_or_none()

    if instrument is None:
        instrument = Instrument(
            code=code,
            name=name,
            type="currency",
            is_active=True,
        )
        db_session.add(instrument)
        await db_session.flush()

    for rate_date, value in (rates or {}).items():
        result = await db_session.execute(
            select(Rate).where(
                Rate.instrument_id == instrument.id,
                Rate.date == rate_date,
            )
        )
        existing_rate = result.scalar_one_or_none()
        if existing_rate is None:
            db_session.add(
                Rate(
                    instrument_id=instrument.id,
                    date=rate_date,
                    rate=value,
                    unit=1,
                    created_at=datetime.now(UTC),
                )
            )
        else:
            existing_rate.rate = value
            existing_rate.unit = 1

    await db_session.flush()
    return instrument


@pytest.mark.asyncio
async def test_get_instruments(client: AsyncClient) -> None:
    response = await client.get("/api/v1/instruments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_instruments_with_page(client: AsyncClient) -> None:
    response = await client.get("/api/v1/instruments?page=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_instrument_rate_history(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await add_instrument_with_rates(
        db_session,
        code="USD",
        name="US Dollar",
        rates={
            date(2026, 10, 1): Decimal("41.00"),
            date(2026, 10, 2): Decimal("41.25"),
        },
    )

    response = await client.get(
        "/api/v1/instruments/USD/rates?from=2026-10-01&to=2026-10-02"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) and len(data) >= 1
    assert data[-1]["date"] == "2026-10-02"
    assert data[-1]["unit"] == 1


@pytest.mark.asyncio
async def test_get_instrument_volatility(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await add_instrument_with_rates(
        db_session,
        code="USD",
        name="US Dollar",
        rates={
            date(2026, 10, 1): Decimal("41.00"),
            date(2026, 10, 2): Decimal("41.25"),
        },
    )

    response = await client.get(
        "/api/v1/instruments/USD/volatility?from=2026-10-01&to=2026-10-02"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "USD"
    assert data["from"] == "2026-10-01"
    assert data["to"] == "2026-10-02"
    assert "volatility" in data


@pytest.mark.asyncio
async def test_compare_instruments(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await add_instrument_with_rates(
        db_session,
        code="USD",
        name="US Dollar",
        rates={
            date(2026, 10, 1): Decimal("41.00"),
            date(2026, 10, 2): Decimal("41.25"),
        },
    )
    await add_instrument_with_rates(
        db_session,
        code="EUR",
        name="Euro",
        rates={
            date(2026, 10, 1): Decimal("47.00"),
            date(2026, 10, 2): Decimal("47.25"),
        },
    )

    response = await client.get(
        "/api/v1/instruments/compare?first=USD&second=EUR&from=2026-10-01&to=2026-10-02"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) and len(data) >= 1
    assert {"date", "first_rate", "second_rate"} <= data[0].keys()


@pytest.mark.asyncio
async def test_get_significant_changes(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await add_instrument_with_rates(
        db_session,
        code="USD",
        name="US Dollar",
        rates={
            date(2026, 10, 1): Decimal("41.00"),
            date(2026, 10, 2): Decimal("42.00"),
        },
    )

    response = await client.get(
        "/api/v1/instruments/USD/significant-changes?from=2026-10-01&to=2026-10-02&threshold=0.01"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert {"date", "rate", "change"} <= data[0].keys()


@pytest.mark.asyncio
async def test_update_instrument_status_requires_admin(
    client: AsyncClient,
) -> None:
    email, password = f"user-status-{uuid4()}@example.com", "test-password-123"
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
    response = await client.patch(
        "/api/v1/instruments/USD/status",
        json={"is_active": False},
    )
    # This test checks authorization before instrument lookup.
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_can_update_instrument_status(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await add_instrument_with_rates(
        db_session,
        code="USD",
        name="US Dollar",
    )
    email, password = f"admin-status-{uuid4()}@example.com", "test-password-123"
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 201

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.role = "admin"
    await db_session.flush()

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200

    response = await client.patch(
        "/api/v1/instruments/USD/status",
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["code"] == "USD"
    assert response.json()["is_active"] is False

    restored = await client.patch(
        "/api/v1/instruments/USD/status",
        json={"is_active": True},
    )
    assert restored.status_code == 200
    assert restored.json()["is_active"] is True


@pytest.mark.asyncio
async def test_admin_update_unknown_instrument(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email, password = f"admin-unknown-{uuid4()}@example.com", "test-password-123"
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 201

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.role = "admin"
    await db_session.flush()

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200

    response = await client.patch(
        "/api/v1/instruments/UNKNOWN/status",
        json={"is_active": False},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Instrument not found"
