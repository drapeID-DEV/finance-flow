from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.rate import Rate
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.sources.nbu import NbuRate


class RateService:
    def __init__(
        self,
        rate_repository: RateRepository,
        instrument_repository: InstrumentRepository,
    ) -> None:
        self.rate_repository = rate_repository
        self.instrument_repository = instrument_repository

    async def save_rate(
        self,
        session: AsyncSession,
        nbu_rate: NbuRate,
        rate_date: date,
    ) -> Rate | None:
        instrument = await self.instrument_repository.get_by_code(
            session,
            nbu_rate.code,
        )

        if instrument is None:
            return None

        existing = await self.rate_repository.get_by_instrument_and_date(
            session,
            instrument.id,
            rate_date,
        )

        if existing is not None:
            return existing

        rate = Rate(
            instrument_id=instrument.id,
            date=rate_date,
            rate=Decimal(nbu_rate.rate),
            unit=nbu_rate.unit,
            created_at=datetime.now(UTC),
        )

        return await self.rate_repository.add(session, rate)