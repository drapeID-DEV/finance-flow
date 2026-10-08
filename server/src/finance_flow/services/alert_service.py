from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.alert import Alert
from finance_flow.repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, repository: AlertRepository) -> None:
        self.repository = repository

    async def create_alert(
        self,
        session: AsyncSession,
        user_id: int,
        instrument_id: int,
        direction: str,
        value: Decimal,
    ) -> Alert:
        if direction not in {"above", "below"}:
            raise ValueError("Invalid alert direction")

        if value <= Decimal("0"):
            raise ValueError("Alert value must be positive")

        alert = Alert(
            user_id=user_id,
            instrument_id=instrument_id,
            direction=direction,
            value=value,
            status="active",
            created_at=datetime.now(UTC),
        )

        return await self.repository.add(session, alert)

    async def get_user_alerts(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[Alert]:
        return await self.repository.get_by_user(
            session,
            user_id=user_id,
        )

    async def check_alerts(
        self,
        session: AsyncSession,
        instrument_id: int,
        current_rate: Decimal,
    ) -> list[Alert]:
        alerts = await self.repository.get_active_by_instrument(
            session,
            instrument_id=instrument_id,
        )

        triggered_alerts: list[Alert] = []
        triggered_at = datetime.now(UTC)

        for alert in alerts:
            should_trigger = (
                alert.direction == "above"
                and current_rate >= alert.value
            ) or (
                alert.direction == "below"
                and current_rate <= alert.value
            )

            if not should_trigger:
                continue

            alert.status = "triggered"
            alert.triggered_at = triggered_at
            triggered_alerts.append(alert)

        await session.flush()

        return triggered_alerts