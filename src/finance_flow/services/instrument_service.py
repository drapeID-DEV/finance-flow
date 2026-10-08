from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.instrument import Instrument
from finance_flow.repositories.instrument_repository import InstrumentRepository


class InstrumentService:
    def __init__(self, repository: InstrumentRepository) -> None:
        self.repository = repository

    async def get_by_code(
        self,
        session: AsyncSession,
        code: str,
    ) -> Instrument | None:
        return await self.repository.get_by_code(session, code)

    async def get_active(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> list[Instrument]:
        return await self.repository.get_active(
            session,
            page=page,
            page_size=page_size,
        )

    async def create(
        self,
        session: AsyncSession,
        instrument: Instrument,
    ) -> Instrument:
        existing = await self.repository.get_by_code(session, instrument.code)

        if existing is not None:
            return existing

        return await self.repository.add(session, instrument)

    async def set_active(
        self,
        session: AsyncSession,
        code: str,
        is_active: bool,
    ) -> Instrument:
        instrument = await self.repository.get_by_code(
            session,
            code,
        )

        if instrument is None:
            raise ValueError("Instrument not found")

        instrument.is_active = is_active
        await session.flush()

        return instrument