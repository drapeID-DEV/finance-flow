from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

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

    @staticmethod
    def _active_filters(
        search: str | None = None,
        instrument_type: str | None = None,
    ) -> list:
        filters: list[ColumnElement[bool]] = [
            Instrument.is_active.is_(True),
        ]

        if search and search.strip():
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Instrument.code.ilike(pattern),
                    Instrument.name.ilike(pattern),
                )
            )

        if instrument_type:
            filters.append(Instrument.type == instrument_type)

        return filters

    async def get_active(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        instrument_type: str | None = None,
    ) -> list[Instrument]:
        offset = (page - 1) * page_size
        filters = self._active_filters(search, instrument_type)

        result = await session.execute(
            select(Instrument)
            .where(*filters)
            .order_by(Instrument.code)
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all())

    async def count_active(
        self,
        session: AsyncSession,
        search: str | None = None,
        instrument_type: str | None = None,
    ) -> int:
        filters = self._active_filters(search, instrument_type)

        result = await session.execute(
            select(func.count())
            .select_from(Instrument)
            .where(*filters)
        )
        return result.scalar_one()

    async def add(
        self,
        session: AsyncSession,
        instrument: Instrument,
    ) -> Instrument:
        session.add(instrument)
        await session.flush()
        return instrument