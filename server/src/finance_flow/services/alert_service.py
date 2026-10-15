
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
        current_rate: Decimal | None = None,
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

        await self.repository.add(session, alert)

        if current_rate is not None:
            await self.check_alerts(
                session,
                instrument_id=instrument_id,
                current_rate=current_rate,
            )

        return alert

    async def update_alert(
        self,
        session: AsyncSession,
        user_id: int,
        alert_id: int,
        direction: str,
        value: Decimal,
        current_rate: Decimal | None = None,
    ) -> Alert | None:
        if direction not in {"above", "below"}:
            raise ValueError("Invalid alert direction")

        if value <= Decimal("0"):
            raise ValueError("Alert value must be positive")

        alert = await self.repository.get_by_id(
            session,
            alert_id=alert_id,
        )

        if alert is None or alert.user_id != user_id:
            return None

        duplicate = await self.repository.exists_duplicate(
            session,
            user_id=user_id,
            instrument_id=alert.instrument_id,
            direction=direction,
            value=value,
            exclude_alert_id=alert.id,
        )

        if duplicate:
            raise ValueError("Alert already exists")

        alert.direction = direction
        alert.value = value

        # Editing an alert reactivates it and clears its previous trigger.
        alert.status = "active"
        alert.triggered_at = None

        await session.flush()

        if current_rate is not None:
            await self.check_alerts(
                session,
                instrument_id=alert.instrument_id,
                current_rate=current_rate,
            )

        return alert

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

    async def delete_alert(
        self,
        session: AsyncSession,
        user_id: int,
        alert_id: int,
    ) -> bool:
        alert = await self.repository.get_by_id(
            session,
            alert_id=alert_id,
        )

        if alert is None or alert.user_id != user_id:
            return False

        await self.repository.delete(session, alert)
        return True
