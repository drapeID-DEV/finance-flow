from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.dependencies import get_db_session
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.services.instrument_service import InstrumentService

router = APIRouter(prefix="/api/v1/instruments", tags=["instruments"])

repository = InstrumentRepository()
service = InstrumentService(repository)


@router.get("")
async def get_instruments(
    page: int = Query(default=1, ge=1),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict[str, object]]:
    instruments = await service.get_active(
        session,
        page=page,
    )

    return [
        {
            "code": instrument.code,
            "name": instrument.name,
            "type": instrument.type,
            "is_active": instrument.is_active,
        }
        for instrument in instruments
    ]