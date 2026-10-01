from datetime import date

import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.dependencies import get_db_session
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.collection_service import CollectionService
from finance_flow.services.rate_service import RateService
from finance_flow.sources.nbu import NbuSource

router = APIRouter(
    prefix="/api/v1/collect",
    tags=["collection"],
)


@router.post("/run")
async def run_collection(
    rate_date: date = Query(...),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, int]:
    async with httpx.AsyncClient() as client:
        source = NbuSource(client)

        instrument_repository = InstrumentRepository()
        rate_repository = RateRepository()

        rate_service = RateService(
            rate_repository=rate_repository,
            instrument_repository=instrument_repository,
        )

        collection_service = CollectionService(
            source=source,
            rate_service=rate_service,
            instrument_repository=instrument_repository,
        )

        saved_count = await collection_service.collect(
            session,
            rate_date,
        )

    return {"saved_count": saved_count}