
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.alert import Alert


class AlertRepository:
    async def get_by_id(
        self,
        session: AsyncSession,
        alert_id: int,
    ) -> Alert | None:
        result = await session.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[Alert]:
        result = await session.execute(
            select(Alert)
            .where(Alert.user_id == user_id)
            .order_by(Alert.id)
        )
        return list(result.scalars().all())

    async def add(
        self,
        session: AsyncSession,
        alert: Alert,
    ) -> Alert:
        session.add(alert)
        await session.flush()
        return alert

    async def get_active_by_instrument(
        self,
        session: AsyncSession,
        instrument_id: int,
    ) -> list[Alert]:
        result = await session.execute(
            select(Alert)
            .where(
                Alert.instrument_id == instrument_id,
                Alert.status == "active",
            )
            .order_by(Alert.id)
        )
        return list(result.scalars().all())

    async def exists_duplicate(
        self,
        session: AsyncSession,
        user_id: int,
        instrument_id: int,
        direction: str,
        value: object,
        exclude_alert_id: int,
    ) -> bool:
        result = await session.execute(
            select(Alert.id)
            .where(
                Alert.user_id == user_id,
                Alert.instrument_id == instrument_id,
                Alert.direction == direction,
                Alert.value == value,
                Alert.id != exclude_alert_id,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def delete(
        self,
        session: AsyncSession,
        alert: Alert,
    ) -> None:
        await session.delete(alert)
        await session.flush()
