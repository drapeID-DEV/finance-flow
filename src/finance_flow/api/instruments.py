from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.dependencies import get_db_session
from finance_flow.repositories.alert_repository import AlertRepository
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.alert_service import AlertService
from finance_flow.services.instrument_service import InstrumentService
from finance_flow.services.rate_service import RateService

router = APIRouter(prefix="/api/v1/instruments", tags=["instruments"])

repository = InstrumentRepository()
service = InstrumentService(repository)
rate_repository = RateRepository()
rate_service = RateService(
    RateRepository(),
    InstrumentRepository(),
    AlertService(AlertRepository()),
)


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


@router.get("/{code}/rates")
async def get_rate_history(
    code: str,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    aggregation: Literal["day", "week", "month"] = Query(
        default="day",
        alias="agg",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict[str, object]]:
    rates = await rate_service.get_history(
        session,
        instrument_code=code,
        from_date=from_date,
        to_date=to_date,
    )

    if aggregation == "day":
        rates = await rate_service.get_history(
            session,
            instrument_code=code,
            from_date=from_date,
            to_date=to_date,
        )

        return [
            {
                "date": rate.date,
                "rate": rate.rate,
                "unit": rate.unit,
            }
            for rate in rates
        ]

    return await rate_service.get_aggregated_history(
        session,
        instrument_code=code,
        from_date=from_date,
        to_date=to_date,
        aggregation=aggregation,
        page=page,
        page_size=page_size,
    )


@router.get("/{code}/volatility")
async def get_volatility(
    code: str,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    volatility = await rate_service.calculate_volatility(
        session,
        instrument_code=code,
        from_date=from_date,
        to_date=to_date,
    )

    return {
        "code": code,
        "from": from_date,
        "to": to_date,
        "volatility": volatility,
    }


@router.get("/compare")
async def compare_instruments(
    first: str = Query(...),
    second: str = Query(...),
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict[str, date | Decimal]]:
    return await rate_service.compare_instruments(
        session,
        first_code=first,
        second_code=second,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/{code}/significant-changes")
async def get_significant_changes(
    code: str,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    threshold: Decimal = Query(..., gt=0),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict[str, date | Decimal]]:
    return await rate_service.find_significant_changes(
        session,
        instrument_code=code,
        from_date=from_date,
        to_date=to_date,
        threshold=threshold,
    )