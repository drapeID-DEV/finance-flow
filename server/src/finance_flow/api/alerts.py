from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.dependencies import get_current_user, get_db_session
from finance_flow.models.user import User
from finance_flow.repositories.alert_repository import AlertRepository
from finance_flow.services.alert_service import AlertService

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["alerts"],
)

alert_service = AlertService(AlertRepository())


class CreateAlertRequest(BaseModel):
    instrument_id: int
    direction: str
    value: Decimal = Field(gt=0)


class AlertResponse(BaseModel):
    id: int
    instrument_id: int
    direction: str
    value: Decimal
    status: str


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_alert(
    request: CreateAlertRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AlertResponse:
    try:
        alert = await alert_service.create_alert(
            session,
            user_id=current_user.id,
            instrument_id=request.instrument_id,
            direction=request.direction,
            value=request.value,
        )

        await session.commit()

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alert already exists",
        ) from exc

    return AlertResponse(
        id=alert.id,
        instrument_id=alert.instrument_id,
        direction=alert.direction,
        value=alert.value,
        status=alert.status,
    )


@router.get(
    "",
    response_model=list[AlertResponse],
)
async def get_alerts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[AlertResponse]:
    alerts = await alert_service.get_user_alerts(
        session,
        user_id=current_user.id,
    )

    return [
        AlertResponse(
            id=alert.id,
            instrument_id=alert.instrument_id,
            direction=alert.direction,
            value=alert.value,
            status=alert.status,
        )
        for alert in alerts
    ]