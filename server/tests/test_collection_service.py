from datetime import date
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.instrument import Instrument
from finance_flow.models.rate import Rate
from finance_flow.repositories.alert_repository import AlertRepository
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.alert_service import AlertService
from finance_flow.services.collection_service import CollectionService
from finance_flow.services.instrument_service import InstrumentService
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuSource


@pytest.mark.asyncio
async def test_collect_rates(db_session: AsyncSession) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json=[
                {
                    "r030": 840,
                    "txt": "Р”РѕР»Р°СЂ РЎРЁРђ",
                    "rate": 41.25,
                    "cc": "COLL01",
                },
            ],
        ),
    )

    async with httpx.AsyncClient(transport=transport) as client:
        source = NbuSource(client)

        instrument_repository = InstrumentRepository()
        rate_repository = RateRepository()
        alert_repository = AlertRepository()
        alert_service = AlertService(alert_repository)

        rate_service = RateService(
            rate_repository=rate_repository,
            instrument_repository=instrument_repository,
            alert_service=alert_service,
        )
        instrument_service = InstrumentService(
            repository=instrument_repository,
        )

        collection_service = CollectionService(
            source=source,
            rate_service=rate_service,
            instrument_service=instrument_service,
        )

        instrument = await instrument_repository.get_by_code(
            db_session,
            "COLL01",
        )
        if instrument is None:
            instrument = Instrument(
                code="COLL01",
                name="Collection Test Instrument",
                type="currency",
                is_active=True,
            )
            db_session.add(instrument)
            await db_session.flush()

        await db_session.execute(
            delete(Rate).where(
                Rate.instrument_id == instrument.id,
                Rate.date == date(2026, 10, 1),
            )
        )
        await db_session.flush()

        saved_count = await collection_service.collect(
            db_session,
            date(2026, 10, 1),
        )

        assert saved_count == 1

        saved_rate = await rate_repository.get_by_instrument_and_date(
            db_session,
            instrument.id,
            date(2026, 10, 1),
        )

        assert saved_rate is not None
        assert saved_rate.rate == Decimal("41.25")
        assert saved_rate.unit == 1

@pytest.mark.asyncio
async def test_collect_without_rates(db_session: AsyncSession) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(404),
    )

    async with httpx.AsyncClient(transport=transport) as client:
        source = NbuSource(client)

        instrument_repository = InstrumentRepository()
        rate_repository = RateRepository()
        alert_repository = AlertRepository()
        alert_service = AlertService(alert_repository)

        rate_service = RateService(
            rate_repository=rate_repository,
            instrument_repository=instrument_repository,
            alert_service=alert_service,
        )
        instrument_service = InstrumentService(
            repository=instrument_repository,
        )

        collection_service = CollectionService(
            source=source,
            rate_service=rate_service,
            instrument_service=instrument_service,
        )

        saved_count = await collection_service.collect(
            db_session,
            date(2026, 10, 4),
        )

        assert saved_count == 0
