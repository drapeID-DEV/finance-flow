
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.dependencies import get_current_user, get_db_session
from finance_flow.models.user import User
from finance_flow.repositories.portfolio_repository import PortfolioRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.portfolio_service import PortfolioService

router = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["portfolio"],
)

portfolio_service = PortfolioService(
    PortfolioRepository(),
    RateRepository(),
)

class AddPortfolioItemRequest(BaseModel):
    quantity: Decimal = Field(default=Decimal("1"), gt=0)

class UpdatePortfolioItemRequest(BaseModel):
    quantity: Decimal = Field(gt=0)


@router.get("")
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    portfolio = await portfolio_service.get_or_create(
        session,
        user_id=current_user.id,
    )

    items = await portfolio_service.get_items(
        session,
        user_id=current_user.id,
    )

    total_value = await portfolio_service.calculate_total_value(
        session,
        user_id=current_user.id,
    )

    instrument_ids = [item.instrument_id for item in items]

    latest_rates = await portfolio_service.rate_repository.get_latest_for_instruments(
        session,
        instrument_ids,
    )

    rates_by_instrument = {
        rate.instrument_id: rate
        for rate in latest_rates
    }

    items_with_rates = []

    for item in items:
        rate = rates_by_instrument.get(item.instrument_id)

        item_value = (
            item.quantity * rate.rate / Decimal(rate.unit)
            if rate is not None and rate.unit > 0
            else None
        )

        items_with_rates.append(
            {
                "instrument_id": item.instrument_id,
                "quantity": item.quantity,
                "current_rate": rate.rate if rate is not None else None,
                "rate_unit": rate.unit if rate is not None else None,
                "rate_date": rate.date if rate is not None else None,
                "value": item_value,
            }
        )

    return {
        "id": portfolio.id,
        "base_currency": portfolio.base_currency,
        "total_value": total_value,
        "items": items_with_rates,
    }


@router.post("/items/{instrument_id}")
async def add_portfolio_item(
    instrument_id: int,
    request: AddPortfolioItemRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    try:
        item = await portfolio_service.add_item(
            session,
            user_id=current_user.id,
            instrument_id=instrument_id,
            quantity=request.quantity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    await session.commit()

    return {
        "instrument_id": item.instrument_id,
        "quantity": item.quantity,
    }


@router.put("/items/{instrument_id}")
async def update_portfolio_item(
    instrument_id: int,
    request: UpdatePortfolioItemRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    try:
        item = await portfolio_service.update_item_quantity(
            session,
            user_id=current_user.id,
            instrument_id=instrument_id,
            quantity=request.quantity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    await session.commit()

    return {
        "instrument_id": item.instrument_id,
        "quantity": item.quantity,
    }


@router.delete("/items/{instrument_id}")
async def delete_portfolio_item(
    instrument_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    try:
        await portfolio_service.delete_item(
            session,
            user_id=current_user.id,
            instrument_id=instrument_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    await session.commit()

    return {
        "message": "Portfolio item deleted",
        "instrument_id": instrument_id,
    }