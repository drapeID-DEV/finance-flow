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
    ) -> list[Instrument]:
        return await self.repository.get_active(session)

    async def create(
        self,
        session: AsyncSession,
        instrument: Instrument,
    ) -> Instrument:
        existing = await self.repository.get_by_code(session, instrument.code)

        if existing is not None:
            return existing

        return await self.repository.add(session, instrument)