

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.dependencies import get_current_user, get_db_session
from finance_flow.models.alert import Alert
from finance_flow.models.instrument import Instrument
from finance_flow.models.portfolio import Portfolio
from finance_flow.models.portfolio_item import PortfolioItem
from finance_flow.models.rate import Rate
from finance_flow.models.user import User

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
)


async def count_rows(session: AsyncSession, model: type) -> int:
    result = await session.execute(
        select(func.count()).select_from(model)
    )
    return result.scalar_one()


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    latest_rate_date = await session.scalar(
        select(func.max(Rate.date))
    )

    active_instruments = await session.scalar(
        select(func.count())
        .select_from(Instrument)
        .where(Instrument.is_active.is_(True))
    )

    if current_user.role == "admin":
        total_users = await count_rows(session, User)

        active_users = await session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.is_active.is_(True))
        )

        total_instruments = await count_rows(session, Instrument)
        total_rates = await count_rows(session, Rate)
        total_alerts = await count_rows(session, Alert)

        return {
            "role": "admin",
            "total_users": total_users,
            "active_users": active_users,
            "total_instruments": total_instruments,
            "active_instruments": active_instruments,
            "total_rates": total_rates,
            "total_alerts": total_alerts,
            "latest_rate_date": latest_rate_date,
        }

    portfolio_items = await session.scalar(
        select(func.count())
        .select_from(PortfolioItem)
        .join(
            Portfolio,
            Portfolio.id == PortfolioItem.portfolio_id,
        )
        .where(Portfolio.user_id == current_user.id)
    )

    active_alerts = await session.scalar(
        select(func.count())
        .select_from(Alert)
        .where(
            Alert.user_id == current_user.id,
            Alert.status == "active",
        )
    )

    triggered_alerts = await session.scalar(
        select(func.count())
        .select_from(Alert)
        .where(
            Alert.user_id == current_user.id,
            Alert.status == "triggered",
        )
    )

    return {
        "role": "user",
        "portfolio_items": portfolio_items,
        "active_alerts": active_alerts,
        "triggered_alerts": triggered_alerts,
        "active_instruments": active_instruments,
        "latest_rate_date": latest_rate_date,
    }
