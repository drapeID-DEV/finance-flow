from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.instrument import Instrument


class InstrumentRepository:
    async def get_by_code(
        self,
        session: AsyncSession,
        code: str,
    ) -> Instrument | None:
        result = await session.execute(
            select(Instrument).where(Instrument.code == code)
        )

        return result.scalar_one_or_none()

    async def get_active(
    self,
    session: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    ) -> list[Instrument]:
        offset = (page - 1) * page_size

        result = await session.execute(
            select(Instrument)
            .where(Instrument.is_active.is_(True))
            .order_by(Instrument.code)
            .offset(offset)
            .limit(page_size)
        )

        return list(result.scalars().all())

    async def add(
        self,
        session: AsyncSession,
        instrument: Instrument,
    ) -> Instrument:
        session.add(instrument)
        await session.flush()

        return instrument