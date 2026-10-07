from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from finance_flow.database import async_session_factory
from finance_flow.models.instrument import Instrument
from finance_flow.models.rate import Rate
from finance_flow.models.user import User
from finance_flow.repositories.portfolio_repository import PortfolioRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.portfolio_service import PortfolioService


@pytest.mark.asyncio
async def test_get_or_create_portfolio() -> None:
    repository = PortfolioRepository()
    rate_repository = RateRepository()
    service = PortfolioService(repository, rate_repository)

    async with async_session_factory() as session:
        user = User(
            email=f"portfolio-create-{uuid4()}@example.com",
            password_hash="test-hash",
            role="user",
            is_active=True,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        await session.flush()

        portfolio = await service.get_or_create(
            session,
            user_id=user.id,
        )

        await session.commit()

        assert portfolio.id is not None
        assert portfolio.user_id == user.id
        assert portfolio.base_currency == "UAH"


@pytest.mark.asyncio
async def test_add_portfolio_item() -> None:
    repository = PortfolioRepository()
    rate_repository = RateRepository()
    service = PortfolioService(repository, rate_repository)

    async with async_session_factory() as session:
        instrument = Instrument(
            code=f"PORT_{uuid4().hex[:8]}",
            name="Portfolio Test",
            type="currency",
            is_active=True,
        )
        session.add(instrument)
        await session.flush()

        user = User(
            email=f"portfolio-test-{uuid4()}@example.com",
            password_hash="test-hash",
            role="user",
            is_active=True,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        await session.flush()

        portfolio = await service.get_or_create(
            session,
            user_id=user.id,
        )

        item = await service.add_item(
            session,
            user_id=user.id,
            instrument_id=instrument.id,
            quantity=Decimal("2"),
        )

        await session.commit()

        assert item.id is not None
        assert item.portfolio_id == portfolio.id
        assert item.instrument_id == instrument.id
        assert item.quantity == Decimal("2")

        item = await service.add_item(
            session,
            user_id=user.id,
            instrument_id=instrument.id,
            quantity=Decimal("3"),
        )

        await session.commit()

        assert item.id is not None
        assert item.quantity == Decimal("5")


@pytest.mark.asyncio
async def test_calculate_total_value() -> None:
    repository = PortfolioRepository()
    rate_repository = RateRepository()
    service = PortfolioService(repository, rate_repository)

    async with async_session_factory() as session:
        instrument = Instrument(
            code=f"VALUE_{uuid4().hex[:8]}",
            name="Value Test",
            type="currency",
            is_active=True,
        )
        session.add(instrument)
        await session.flush()

        user = User(
            email=f"value-test-{uuid4()}@example.com",
            password_hash="test-hash",
            role="user",
            is_active=True,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        await session.flush()

        portfolio = await service.get_or_create(
            session,
            user_id=user.id,
        )

        await service.add_item(
            session,
            user_id=user.id,
            instrument_id=instrument.id,
            quantity=Decimal("10"),
        )

        rate = Rate(
            instrument_id=instrument.id,
            date=date.today(),
            rate=Decimal("4200"),
            unit=100,
            created_at=datetime.now(UTC),
        )
        session.add(rate)

        await session.commit()

        total_value = await service.calculate_total_value(
            session,
            user_id=user.id,
        )

        assert portfolio.id is not None
        assert total_value == Decimal("420")