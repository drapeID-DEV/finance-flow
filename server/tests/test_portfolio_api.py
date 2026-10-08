from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from finance_flow.database import async_session_factory
from finance_flow.main import app
from finance_flow.models.instrument import Instrument
from finance_flow.models.rate import Rate
from finance_flow.models.user import User
from finance_flow.repositories.portfolio_repository import PortfolioRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.portfolio_service import PortfolioService

client = TestClient(app)


def test_get_portfolio_requires_authentication() -> None:
    response = client.get("/api/v1/portfolio")

    assert response.status_code == 401


def test_get_portfolio() -> None:
    email = f"portfolio-api-{uuid4()}@example.com"
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

    response = client.get(
        "/api/v1/portfolio",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["base_currency"] == "UAH"
    assert data["total_value"] == "0"
    assert data["items"] == []


@pytest.mark.asyncio
async def test_get_portfolio_with_item() -> None:
    email = f"portfolio-item-{uuid4()}@example.com"
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

    async with async_session_factory() as session:
        user_result = await session.execute(
            select(User).where(User.email == email)
        )
        user = user_result.scalar_one()

        instrument = Instrument(
            code=f"API_{uuid4().hex[:8]}",
            name="API Portfolio Test",
            type="currency",
            is_active=True,
        )
        session.add(instrument)
        await session.flush()

        rate = Rate(
            instrument_id=instrument.id,
            date=date.today(),
            rate=Decimal("4200"),
            unit=100,
            created_at=datetime.now(UTC),
        )
        session.add(rate)

        service = PortfolioService(
            PortfolioRepository(),
            RateRepository(),
        )

        await service.add_item(
            session,
            user_id=user.id,
            instrument_id=instrument.id,
            quantity=Decimal("10"),
        )

        await session.commit()

    response = client.get(
        "/api/v1/portfolio",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["base_currency"] == "UAH"
    assert Decimal(data["total_value"]) == Decimal("420")
    assert len(data["items"]) == 1
    assert Decimal(data["items"][0]["quantity"]) == Decimal("10")


@pytest.mark.asyncio
async def test_update_portfolio_item_quantity() -> None:
    email = f"portfolio-update-{uuid4()}@example.com"
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

    async with async_session_factory() as session:
        user_result = await session.execute(
            select(User).where(User.email == email)
        )
        user = user_result.scalar_one()

        instrument = Instrument(
            code=f"UPDATE_{uuid4().hex[:8]}",
            name="Update Portfolio Test",
            type="currency",
            is_active=True,
        )
        session.add(instrument)
        await session.flush()

        service = PortfolioService(
            PortfolioRepository(),
            RateRepository(),
        )

        await service.add_item(
            session,
            user_id=user.id,
            instrument_id=instrument.id,
            quantity=Decimal("10"),
        )

        await session.commit()

        instrument_id = instrument.id

    response = client.put(
        f"/api/v1/portfolio/items/{instrument_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "quantity": "25",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["instrument_id"] == instrument_id
    assert Decimal(data["quantity"]) == Decimal("25")


@pytest.mark.asyncio
async def test_delete_portfolio_item() -> None:
    email = f"portfolio-delete-{uuid4()}@example.com"
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

    async with async_session_factory() as session:
        user_result = await session.execute(
            select(User).where(User.email == email)
        )
        user = user_result.scalar_one()

        instrument = Instrument(
            code=f"DELETE_{uuid4().hex[:8]}",
            name="Delete Portfolio Test",
            type="currency",
            is_active=True,
        )
        session.add(instrument)
        await session.flush()

        service = PortfolioService(
            PortfolioRepository(),
            RateRepository(),
        )

        await service.add_item(
            session,
            user_id=user.id,
            instrument_id=instrument.id,
            quantity=Decimal("10"),
        )

        await session.commit()

        instrument_id = instrument.id

    response = client.delete(
        f"/api/v1/portfolio/items/{instrument_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["instrument_id"] == instrument_id
    assert data["message"] == "Portfolio item deleted"

    portfolio_response = client.get(
        "/api/v1/portfolio",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert portfolio_response.status_code == 200
    assert portfolio_response.json()["items"] == []