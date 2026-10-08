from datetime import date

import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.dependencies import get_db_session
from finance_flow.repositories.alert_repository import AlertRepository
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.alert_service import AlertService
from finance_flow.services.collection_service import CollectionService
from finance_flow.services.instrument_service import InstrumentService
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuSource

router = APIRouter(
    prefix="/api/v1/collect",
    tags=["collection"],
)


@router.post("/run")
async def run_collection(
    collection_date: date = Query(..., alias="date"),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, int]:
    async with httpx.AsyncClient() as client:
        source = NbuSource(client)

        instrument_repository = InstrumentRepository()

        rate_service = RateService(
            RateRepository(),
            InstrumentRepository(),
            AlertService(AlertRepository()),
        )

        instrument_service = InstrumentService(
            repository=instrument_repository,
        )

        collection_service = CollectionService(
            source=source,
            rate_service=rate_service,
            instrument_service=instrument_service,
        )

        saved_count = await collection_service.collect(session, collection_date)

    return {"saved_count": saved_count}