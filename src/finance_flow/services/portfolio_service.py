from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.portfolio import Portfolio
from finance_flow.models.portfolio_item import PortfolioItem
from finance_flow.repositories.portfolio_repository import PortfolioRepository
from finance_flow.repositories.rate_repository import RateRepository


class PortfolioService:
    def __init__(
        self,
        repository: PortfolioRepository,
        rate_repository: RateRepository,
    ) -> None:
        self.repository = repository
        self.rate_repository = rate_repository

    async def get_or_create(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Portfolio:
        portfolio = await self.repository.get_by_user_id(
            session,
            user_id,
        )

        if portfolio is not None:
            return portfolio

        portfolio = Portfolio(
            user_id=user_id,
            base_currency="UAH",
            created_at=datetime.now(UTC),
        )

        return await self.repository.add(session, portfolio)

    async def get_items(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[PortfolioItem]:
        portfolio = await self.get_or_create(
            session,
            user_id,
        )

        return await self.repository.get_items(
            session,
            portfolio.id,
        )

    async def add_item(
        self,
        session: AsyncSession,
        user_id: int,
        instrument_id: int,
        quantity: Decimal = Decimal("1"),
    ) -> PortfolioItem:
        portfolio = await self.get_or_create(
            session,
            user_id,
        )

        existing_item = await self.repository.get_item(
            session,
            portfolio.id,
            instrument_id,
        )

        if existing_item is not None:
            existing_item.quantity += quantity
            await session.flush()
            return existing_item

        item = PortfolioItem(
            portfolio_id=portfolio.id,
            instrument_id=instrument_id,
            quantity=quantity,
        )

        return await self.repository.add_item(
            session,
            item,
        )

    async def update_item_quantity(
        self,
        session: AsyncSession,
        user_id: int,
        instrument_id: int,
        quantity: Decimal,
    ) -> PortfolioItem:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        portfolio = await self.get_or_create(
            session,
            user_id,
        )

        item = await self.repository.get_item(
            session,
            portfolio.id,
            instrument_id,
        )

        if item is None:
            raise ValueError("Instrument is not in portfolio")

        return await self.repository.update_item_quantity(
            session,
            item,
            quantity,
        )

    async def delete_item(
        self,
        session: AsyncSession,
        user_id: int,
        instrument_id: int,
    ) -> None:
        portfolio = await self.get_or_create(
            session,
            user_id,
        )

        item = await self.repository.get_item(
            session,
            portfolio.id,
            instrument_id,
        )

        if item is None:
            raise ValueError("Instrument is not in portfolio")

        await self.repository.delete_item(
            session,
            item,
        )

    async def calculate_total_value(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Decimal:
        items = await self.get_items(
            session,
            user_id=user_id,
        )

        total_value = Decimal("0")

        for item in items:
            rate = await self.rate_repository.get_latest_by_instrument(
                session,
                instrument_id=item.instrument_id,
            )

            if rate is None:
                continue

            total_value += item.quantity * rate.rate / Decimal(rate.unit)

        return total_value