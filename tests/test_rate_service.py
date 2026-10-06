from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import delete

from finance_flow.database import async_session_factory
from finance_flow.models.rate import Rate
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

        await session.execute(
            delete(Rate).where(
                Rate.instrument_id == instrument.id,
                Rate.date == date(2026, 10, 1),
            )
        )
        await session.commit()

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

        assert saved_again is None     

        saved_rates = await rate_repository.get_by_instrument_and_date(
            session,
            instrument.id,
            date(2026, 10, 1),
        )

        assert saved_rates is not None
        assert saved_rates.id == saved.id


async def test_get_aggregated_history() -> None:
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

        await session.execute(
            delete(Rate).where(
                Rate.instrument_id == instrument.id,
                Rate.date >= date(2026, 9, 28),
                Rate.date <= date(2026, 9, 30),
            )
        )
        await session.commit()

        test_rates = [
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 9, 28),
                rate=Decimal("40"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 9, 29),
                rate=Decimal("42"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 9, 30),
                rate=Decimal("41"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
        ]

        for rate in test_rates:
            await rate_repository.add(session, rate)

        await session.commit()

        result = await service.get_aggregated_history(
            session,
            instrument_code="RTST01",
            from_date=date(2026, 9, 28),
            to_date=date(2026, 9, 30),
            aggregation="week",
        )

        assert len(result) == 1

        period = result[0]

        assert period["open"] == Decimal("40")
        assert period["close"] == Decimal("41")
        assert period["min"] == Decimal("40")
        assert period["max"] == Decimal("42")
        assert period["avg"] == Decimal("41")
        assert period["unit"] == 1