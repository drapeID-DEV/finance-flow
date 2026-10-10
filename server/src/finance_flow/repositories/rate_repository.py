from datetime import date

from sqlalchemy import func, select
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

    async def get_history(
        self,
        session: AsyncSession,
        instrument_id: int,
        from_date: date,
        to_date: date,
    ) -> list[Rate]:
        result = await session.execute(
            select(Rate)
            .where(
                Rate.instrument_id == instrument_id,
                Rate.date >= from_date,
                Rate.date <= to_date,
            )
            .order_by(Rate.date.asc())
        )
        return list(result.scalars().all())

    async def add(
        self,
        session: AsyncSession,
        rate: Rate,
    ) -> Rate:
        session.add(rate)
        await session.flush()
        return rate

    async def get_latest_by_instrument(
        self,
        session: AsyncSession,
        instrument_id: int,
    ) -> Rate | None:
        result = await session.execute(
            select(Rate)
            .where(Rate.instrument_id == instrument_id)
            .order_by(Rate.date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_for_instruments(
        self,
        session: AsyncSession,
        instrument_ids: list[int],
    ) -> list[Rate]:
        if not instrument_ids:
            return []

        latest_dates = (
            select(
                Rate.instrument_id.label("instrument_id"),
                func.max(Rate.date).label("latest_date"),
            )
            .where(Rate.instrument_id.in_(instrument_ids))
            .group_by(Rate.instrument_id)
            .subquery()
        )

        result = await session.execute(
            select(Rate)
            .join(
                latest_dates,
                (Rate.instrument_id == latest_dates.c.instrument_id)
                & (Rate.date == latest_dates.c.latest_date),
            )
        )

        return list(result.scalars().all())

    async def get_history_for_instruments(
        self,
        session: AsyncSession,
        instrument_ids: list[int],
        from_date: date,
        to_date: date,
    ) -> list[Rate]:
        if not instrument_ids:
            return []

        result = await session.execute(
            select(Rate)
            .where(
                Rate.instrument_id.in_(instrument_ids),
                Rate.date >= from_date,
                Rate.date <= to_date,
            )
            .order_by(Rate.date.asc(), Rate.instrument_id.asc())
        )
        return list(result.scalars().all())
