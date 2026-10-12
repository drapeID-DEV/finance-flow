
from datetime import date

import httpx

from finance_flow.database import async_session_factory
from finance_flow.repositories.alert_repository import AlertRepository
from finance_flow.repositories.instrument_repository import (
    InstrumentRepository,
)
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.alert_service import AlertService
from finance_flow.services.collection_service import CollectionService
from finance_flow.services.instrument_service import InstrumentService
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuSource


async def run_collection(rate_date: date) -> int:
    async with httpx.AsyncClient(timeout=30.0) as client:
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

        async with async_session_factory() as session:
            return await collection_service.collect(
                session,
                rate_date,
            )
