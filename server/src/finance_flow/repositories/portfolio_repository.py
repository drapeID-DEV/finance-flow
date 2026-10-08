from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.portfolio import Portfolio
from finance_flow.models.portfolio_item import PortfolioItem


class PortfolioRepository:
    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Portfolio | None:
        result = await session.execute(
            select(Portfolio).where(Portfolio.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def add(
        self,
        session: AsyncSession,
        portfolio: Portfolio,
    ) -> Portfolio:
        session.add(portfolio)
        await session.flush()
        return portfolio

    async def get_item(
        self,
        session: AsyncSession,
        portfolio_id: int,
        instrument_id: int,
    ) -> PortfolioItem | None:
        result = await session.execute(
            select(PortfolioItem).where(
                PortfolioItem.portfolio_id == portfolio_id,
                PortfolioItem.instrument_id == instrument_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_items(
        self,
        session: AsyncSession,
        portfolio_id: int,
    ) -> list[PortfolioItem]:
        result = await session.execute(
            select(PortfolioItem)
            .where(PortfolioItem.portfolio_id == portfolio_id)
            .order_by(PortfolioItem.id)
        )
        return list(result.scalars().all())

    async def add_item(
        self,
        session: AsyncSession,
        item: PortfolioItem,
    ) -> PortfolioItem:
        session.add(item)
        await session.flush()
        return item

    async def update_item_quantity(
        self,
        session: AsyncSession,
        item: PortfolioItem,
        quantity: Decimal,
    ) -> PortfolioItem:
        item.quantity = quantity
        await session.flush()
        return item

    async def delete_item(
        self,
        session: AsyncSession,
        item: PortfolioItem,
    ) -> None:
        await session.delete(item)
        await session.flush()