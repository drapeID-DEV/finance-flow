
from fastapi import APIRouter, Depends
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

    return {
        "id": portfolio.id,
        "base_currency": portfolio.base_currency,
        "total_value": total_value,
        "items": [
            {
                "instrument_id": item.instrument_id,
                "quantity": item.quantity,
            }
            for item in items
        ],
    }