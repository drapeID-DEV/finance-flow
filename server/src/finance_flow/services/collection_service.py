from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.instrument import Instrument
from finance_flow.services.instrument_service import InstrumentService
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuSource

METAL_CODES = {"XAU", "XAG", "XPT", "XPD"}


def get_instrument_type(code: str) -> str:
    return "metal" if code.upper() in METAL_CODES else "currency"


class CollectionService:
    def __init__(
        self,
        source: NbuSource,
        rate_service: RateService,
        instrument_service: InstrumentService,
    ) -> None:
        self.source = source
        self.rate_service = rate_service
        self.instrument_service = instrument_service

    async def collect(
        self,
        session: AsyncSession,
        rate_date: date,
    ) -> int:
        rates = await self.source.get_rates(
            rate_date.strftime("%Y%m%d"),
        )

        saved_count = 0

        for nbu_rate in rates:
            instrument = Instrument(
                code=nbu_rate.code,
                name=nbu_rate.name,
                type=get_instrument_type(nbu_rate.code),
                is_active=True,
            )

            await self.instrument_service.create(
                session,
                instrument,
            )

            saved = await self.rate_service.save_rate(
                session,
                nbu_rate,
                rate_date,
            )

            if saved is not None:
                saved_count += 1

        await session.commit()

        return saved_count