from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuSource


class CollectionService:
    def __init__(
        self,
        source: NbuSource,
        rate_service: RateService,
        instrument_repository: InstrumentRepository,
    ) -> None:
        self.source = source
        self.rate_service = rate_service
        self.instrument_repository = instrument_repository

    async def collect(
        self,
        session: AsyncSession,
        rate_date: date,
    ) -> int:
        rates = await self.source.get_rates(
            rate_date.strftime("%d.%m.%Y"),
        )

        saved_count = 0

        for nbu_rate in rates:
            saved = await self.rate_service.save_rate(
                session,
                nbu_rate,
                rate_date,
            )

            if saved is not None:
                saved_count += 1

        await session.commit()

        return saved_count