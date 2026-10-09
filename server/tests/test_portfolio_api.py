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
from finance_flow.repositories.portfolio_repository import PortfolioRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.portfolio_service import PortfolioService


@pytest.mark.asyncio
async def test_get_portfolio_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/portfolio")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_portfolio(client: AsyncClient) -> None:
    email, password = f"portfolio-api-{uuid4()}@example.com", "test-password-123"
    register = await client.post("/api/v1/auth/register", json={
        "email": email, "password": password
    })
    assert register.status_code == 201
    login = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password
    })
    assert login.status_code == 200

    response = await client.get("/api/v1/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["base_currency"] == "UAH"
    assert data["total_value"] == "0"
    assert data["items"] == []


@pytest.mark.asyncio
async def test_get_portfolio_with_item(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email, password = f"portfolio-item-{uuid4()}@example.com", "test-password-123"
    register = await client.post("/api/v1/auth/register", json={
        "email": email, "password": password
    })
    assert register.status_code == 201
    login = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password
    })
    assert login.status_code == 200
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    instrument = Instrument(
        code=f"API_{uuid4().hex[:8]}", name="API Portfolio Test",
        type="currency", is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()
    db_session.add(Rate(
        instrument_id=instrument.id, date=date.today(),
        rate=Decimal("4200"), unit=100, created_at=datetime.now(UTC),
    ))
    service = PortfolioService(PortfolioRepository(), RateRepository())
    await service.add_item(
        db_session, user_id=user.id, instrument_id=instrument.id,
        quantity=Decimal("10"),
    )
    await db_session.flush()

    response = await client.get("/api/v1/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["base_currency"] == "UAH"
    assert Decimal(data["total_value"]) == Decimal("420")
    assert len(data["items"]) == 1
    assert Decimal(data["items"][0]["quantity"]) == Decimal("10")


@pytest.mark.asyncio
async def test_update_portfolio_item_quantity(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email, password = f"portfolio-update-{uuid4()}@example.com", "test-password-123"
    register = await client.post("/api/v1/auth/register", json={
        "email": email, "password": password
    })
    assert register.status_code == 201
    login = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password
    })
    assert login.status_code == 200
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    instrument = Instrument(
        code=f"UPDATE_{uuid4().hex[:8]}", name="Update Portfolio Test",
        type="currency", is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()
    service = PortfolioService(PortfolioRepository(), RateRepository())
    await service.add_item(
        db_session, user_id=user.id, instrument_id=instrument.id,
        quantity=Decimal("10"),
    )
    await db_session.flush()

    response = await client.put(
        f"/api/v1/portfolio/items/{instrument.id}", json={"quantity": "25"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["instrument_id"] == instrument.id
    assert Decimal(data["quantity"]) == Decimal("25")


@pytest.mark.asyncio
async def test_delete_portfolio_item(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email, password = f"portfolio-delete-{uuid4()}@example.com", "test-password-123"
    register = await client.post("/api/v1/auth/register", json={
        "email": email, "password": password
    })
    assert register.status_code == 201
    login = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password
    })
    assert login.status_code == 200
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    instrument = Instrument(
        code=f"DELETE_{uuid4().hex[:8]}", name="Delete Portfolio Test",
        type="currency", is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()
    service = PortfolioService(PortfolioRepository(), RateRepository())
    await service.add_item(
        db_session, user_id=user.id, instrument_id=instrument.id,
        quantity=Decimal("10"),
    )
    await db_session.flush()

    response = await client.delete(f"/api/v1/portfolio/items/{instrument.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["instrument_id"] == instrument.id
    assert data["message"] == "Portfolio item deleted"

    portfolio_response = await client.get("/api/v1/portfolio")
    assert portfolio_response.status_code == 200
    assert portfolio_response.json()["items"] == []
