from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.rate import Rate


class RateRepository:
    async def get_by_instrument_and_date(
        self,
        session: AsyncSession,
        instrument_id: int,
        rate_date: date,
    ) -> Rate | None:
        result = await session.execute(
            select(Rate).where(
                Rate.instrument_id == instrument_id,
                Rate.date == rate_date,
            )
        )
        return result.scalar_one_or_none()

    async def add(
        self,
        session: AsyncSession,
        rate: Rate,
    ) -> Rate:
        session.add(rate)
        await session.flush()
        return rate