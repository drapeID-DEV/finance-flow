from datetime import date
from decimal import Decimal

import httpx
from sqlalchemy import delete

from finance_flow.database import async_session_factory
from finance_flow.models.rate import Rate
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.collection_service import CollectionService
from finance_flow.services.instrument_service import InstrumentService
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuSource


async def test_collect_rates() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json=[
                {
                    "r030": 840,
                    "txt": "Долар США",
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
        rate_service = RateService(
            rate_repository=rate_repository,
            instrument_repository=instrument_repository,
        )
        instrument_service = InstrumentService(
            repository=instrument_repository,
        )

        collection_service = CollectionService(
            source=source,
            rate_service=rate_service,
            instrument_service=instrument_service,
        )

        async with async_session_factory() as session:
            instrument = await instrument_repository.get_by_code(
                session,
                "COLL01",
            )

            assert instrument is not None

            await session.execute(
                delete(Rate).where(
                    Rate.instrument_id == instrument.id,
                    Rate.date == date(2026, 10, 1),
                )
            )
            await session.commit()

            saved_count = await collection_service.collect(
                session,
                date(2026, 10, 1),
            )

            assert saved_count == 1

            saved_rate = await rate_repository.get_by_instrument_and_date(
                session,
                instrument.id,
                date(2026, 10, 1),
            )

            assert saved_rate is not None
            assert saved_rate.rate == Decimal("41.25")
            assert saved_rate.unit == 1

async def test_collect_without_rates() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(404),
    )

    async with httpx.AsyncClient(transport=transport) as client:
        source = NbuSource(client)

        instrument_repository = InstrumentRepository()
        rate_repository = RateRepository()
        rate_service = RateService(
            rate_repository=rate_repository,
            instrument_repository=instrument_repository,
        )
        instrument_service = InstrumentService(
            repository=instrument_repository,
        )

        collection_service = CollectionService(
            source=source,
            rate_service=rate_service,
            instrument_service=instrument_service,
        )

        async with async_session_factory() as session:
            saved_count = await collection_service.collect(
                session,
                date(2026, 10, 4),
            )

            assert saved_count == 0