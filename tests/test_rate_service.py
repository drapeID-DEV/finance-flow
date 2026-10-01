from datetime import date
from decimal import Decimal

from finance_flow.database import async_session_factory
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuRate


async def test_save_rate() -> None:
    instrument_repository = InstrumentRepository()
    rate_repository = RateRepository()

    service = RateService(
        rate_repository=rate_repository,
        instrument_repository=instrument_repository,
    )

    async with async_session_factory() as session:
        instrument = await instrument_repository.get_by_code(
            session,
            "RTST01",
        )

        assert instrument is not None

        await instrument_repository.add(session, instrument)

        nbu_rate = NbuRate(
            code="RTST01",
            name="Test Dollar",
            rate=Decimal("41.25"),
            unit=1,
        )

        saved = await service.save_rate(
            session,
            nbu_rate,
            date(2026, 10, 1),
        )

        await session.commit()

        assert saved is not None
        assert saved.rate == 41.25
        assert saved.unit == 1

        saved_again = await service.save_rate(
            session,
            nbu_rate,
            date(2026, 10, 1),
        )

        assert saved_again is not None
        assert saved_again.id == saved.id

        saved_rates = await rate_repository.get_by_instrument_and_date(
            session,
            instrument.id,
            date(2026, 10, 1),
        )

        assert saved_rates is not None
        assert saved_rates.id == saved.id