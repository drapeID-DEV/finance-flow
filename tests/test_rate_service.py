import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import delete

from finance_flow.database import async_session_factory
from finance_flow.models.alert import Alert
from finance_flow.models.instrument import Instrument
from finance_flow.models.rate import Rate
from finance_flow.models.user import User
from finance_flow.repositories.alert_repository import AlertRepository
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.alert_service import AlertService
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuRate


async def test_save_rate() -> None:
    instrument_repository = InstrumentRepository()
    rate_repository = RateRepository()
    alert_repository = AlertRepository()
    alert_service = AlertService(alert_repository)

    service = RateService(
        rate_repository=rate_repository,
        instrument_repository=instrument_repository,
        alert_service=alert_service,
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
    alert_repository = AlertRepository()
    alert_service = AlertService(alert_repository)

    service = RateService(
        rate_repository=rate_repository,
        instrument_repository=instrument_repository,
        alert_service=alert_service,
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

@pytest.mark.asyncio
async def test_save_rate_triggers_alert() -> None:
    instrument_repository = InstrumentRepository()
    rate_repository = RateRepository()
    alert_repository = AlertRepository()
    alert_service = AlertService(alert_repository)

    service = RateService(
        rate_repository=rate_repository,
        instrument_repository=instrument_repository,
        alert_service=alert_service,
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
                Rate.date == date(2026, 10, 7),
            )
        )
        await session.commit()

        user = User(
            email=f"rate-alert-{datetime.now(UTC).timestamp()}@example.com",
            password_hash="test-hash",
            role="user",
            is_active=True,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        await session.flush()

        alert = Alert(
            user_id=user.id,
            instrument_id=instrument.id,
            direction="above",
            value=Decimal("40"),
            status="active",
            created_at=datetime.now(UTC),
        )
        session.add(alert)
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
            date(2026, 10, 7),
        )

        await session.commit()

        assert saved is not None

        await session.refresh(alert)

        assert alert.status == "triggered"
        assert alert.triggered_at is not None

        triggered_at = alert.triggered_at

        await session.execute(
            delete(Rate).where(
                Rate.instrument_id == instrument.id,
                Rate.date == date(2026, 10, 8),
            )
        )
        await session.commit()

        second_rate = NbuRate(
            code="RTST01",
            name="Test Dollar",
            rate=Decimal("45"),
            unit=1,
        )

        saved_again = await service.save_rate(
            session,
            second_rate,
            date(2026, 10, 8),
        )

        await session.commit()

        assert saved_again is not None

        await session.refresh(alert)

        assert alert.status == "triggered"
        assert alert.triggered_at == triggered_at

@pytest.mark.asyncio
async def test_calculate_volatility() -> None:
    instrument_repository = InstrumentRepository()
    rate_repository = RateRepository()
    alert_repository = AlertRepository()
    alert_service = AlertService(alert_repository)

    service = RateService(
        rate_repository=rate_repository,
        instrument_repository=instrument_repository,
        alert_service=alert_service,
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
                Rate.date >= date(2026, 10, 10),
                Rate.date <= date(2026, 10, 12),
            )
        )
        await session.commit()

        test_rates = [
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 10, 10),
                rate=Decimal("40"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 10, 11),
                rate=Decimal("45"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 10, 12),
                rate=Decimal("42"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
        ]

        for rate in test_rates:
            await rate_repository.add(session, rate)

        await session.commit()

        volatility = await service.calculate_volatility(
            session,
            instrument_code="RTST01",
            from_date=date(2026, 10, 10),
            to_date=date(2026, 10, 12),
        )

        assert volatility == Decimal("5")

async def test_compare_instruments() -> None:
    async with async_session_factory() as session:
        first_code = f"USD-{uuid.uuid4().hex[:6]}"
        second_code = f"EUR-{uuid.uuid4().hex[:6]}"

        first_instrument = Instrument(
            code=first_code,
            name="Test USD",
            type="currency",
            is_active=True,
        )
        second_instrument = Instrument(
            code=second_code,
            name="Test EUR",
            type="currency",
            is_active=True,
        )

        session.add_all([first_instrument, second_instrument])
        await session.flush()

        session.add_all(
            [
                Rate(
                    instrument_id=first_instrument.id,
                    date=date(2026, 10, 10),
                    rate=Decimal("40"),
                    unit=1,
                    created_at=datetime.now(UTC),
                ),
                Rate(
                    instrument_id=second_instrument.id,
                    date=date(2026, 10, 10),
                    rate=Decimal("45"),
                    unit=1,
                    created_at=datetime.now(UTC),
                ),
                Rate(
                    instrument_id=first_instrument.id,
                    date=date(2026, 10, 11),
                    rate=Decimal("41"),
                    unit=1,
                    created_at=datetime.now(UTC),
                ),
                Rate(
                    instrument_id=second_instrument.id,
                    date=date(2026, 10, 11),
                    rate=Decimal("46"),
                    unit=1,
                    created_at=datetime.now(UTC),
                ),
            ]
        )
        await session.commit()

        service = RateService(
            RateRepository(),
            InstrumentRepository(),
            AlertService(AlertRepository()),
        )

        result = await service.compare_instruments(
            session,
            first_code,
            second_code,
            date(2026, 10, 10),
            date(2026, 10, 11),
        )

        assert len(result) == 2
        assert result[0]["date"] == date(2026, 10, 10)
        assert result[0]["first_rate"] == Decimal("40")
        assert result[0]["second_rate"] == Decimal("45")
        assert result[1]["first_rate"] == Decimal("41")
        assert result[1]["second_rate"] == Decimal("46")

async def test_find_significant_changes() -> None:
    async with async_session_factory() as session:
        instrument_code = f"USD-{uuid.uuid4().hex[:6]}"

        instrument = Instrument(
            code=instrument_code,
            name="Test USD",
            type="currency",
            is_active=True,
        )

        session.add(instrument)
        await session.flush()

        session.add_all(
            [
                Rate(
                    instrument_id=instrument.id,
                    date=date(2026, 10, 10),
                    rate=Decimal("40"),
                    unit=1,
                    created_at=datetime.now(UTC),
                ),
                Rate(
                    instrument_id=instrument.id,
                    date=date(2026, 10, 11),
                    rate=Decimal("41"),
                    unit=1,
                    created_at=datetime.now(UTC),
                ),
                Rate(
                    instrument_id=instrument.id,
                    date=date(2026, 10, 12),
                    rate=Decimal("45"),
                    unit=1,
                    created_at=datetime.now(UTC),
                ),
            ]
        )
        await session.commit()

        service = RateService(
            RateRepository(),
            InstrumentRepository(),
            AlertService(AlertRepository()),
        )

        result = await service.find_significant_changes(
            session,
            instrument_code,
            date(2026, 10, 10),
            date(2026, 10, 12),
            Decimal("0.05"),
        )

        assert len(result) == 1
        assert result[0]["date"] == date(2026, 10, 12)
        assert result[0]["rate"] == Decimal("45")
        assert result[0]["change"] == Decimal("4") / Decimal("41")