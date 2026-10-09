from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.instrument import Instrument
from finance_flow.models.user import User
from finance_flow.repositories.alert_repository import AlertRepository
from finance_flow.services.alert_service import AlertService


@pytest.mark.asyncio
async def test_create_alert(db_session: AsyncSession) -> None:
    repository = AlertRepository()
    service = AlertService(repository)

    instrument = Instrument(
        code=f"ALERT_{uuid4().hex[:8]}",
        name="Alert Test",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    user = User(
        email=f"alert-test-{uuid4()}@example.com",
        password_hash="test-hash",
        role="user",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.flush()

    alert = await service.create_alert(
        db_session,
        user_id=user.id,
        instrument_id=instrument.id,
        direction="above",
        value=Decimal("42.50"),
    )

    await db_session.flush()

    assert alert.id is not None
    assert alert.user_id == user.id
    assert alert.instrument_id == instrument.id
    assert alert.direction == "above"
    assert alert.value == Decimal("42.50")
    assert alert.status == "active"
    assert alert.triggered_at is None


@pytest.mark.asyncio
async def test_get_user_alerts(db_session: AsyncSession) -> None:
    repository = AlertRepository()
    service = AlertService(repository)

    instrument = Instrument(
        code=f"ALERT_{uuid4().hex[:8]}",
        name="Alert Test",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    user = User(
        email=f"alert-list-{uuid4()}@example.com",
        password_hash="test-hash",
        role="user",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.flush()

    await service.create_alert(
        db_session,
        user_id=user.id,
        instrument_id=instrument.id,
        direction="above",
        value=Decimal("42"),
    )

    await service.create_alert(
        db_session,
        user_id=user.id,
        instrument_id=instrument.id,
        direction="below",
        value=Decimal("35"),
    )

    await db_session.flush()

    alerts = await service.get_user_alerts(
        db_session,
        user_id=user.id,
    )

    assert len(alerts) == 2
    assert alerts[0].direction == "above"
    assert alerts[1].direction == "below"


@pytest.mark.asyncio
async def test_create_alert_rejects_invalid_direction(db_session: AsyncSession) -> None:
    repository = AlertRepository()
    service = AlertService(repository)

    with pytest.raises(ValueError, match="Invalid alert direction"):
        await service.create_alert(
            db_session,
            user_id=1,
            instrument_id=1,
            direction="equal",
            value=Decimal("42"),
        )


@pytest.mark.asyncio
async def test_create_alert_rejects_non_positive_value(
    db_session: AsyncSession
) -> None:
    repository = AlertRepository()
    service = AlertService(repository)

    with pytest.raises(ValueError, match="Alert value must be positive"):
        await service.create_alert(
            db_session,
            user_id=1,
            instrument_id=1,
            direction="above",
            value=Decimal("0"),
        )


@pytest.mark.asyncio
async def test_check_alerts_above(db_session: AsyncSession) -> None:
    repository = AlertRepository()
    service = AlertService(repository)

    instrument = Instrument(
        code=f"ALERT_{uuid4().hex[:8]}",
        name="Alert Above Test",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    user = User(
        email=f"alert-above-{uuid4()}@example.com",
        password_hash="test-hash",
        role="user",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.flush()

    alert = await service.create_alert(
        db_session,
        user_id=user.id,
        instrument_id=instrument.id,
        direction="above",
        value=Decimal("42"),
    )

    triggered = await service.check_alerts(
        db_session,
        instrument_id=instrument.id,
        current_rate=Decimal("43"),
    )

    await db_session.flush()

    assert len(triggered) == 1
    assert triggered[0].id == alert.id
    assert alert.status == "triggered"
    assert alert.triggered_at is not None


@pytest.mark.asyncio
async def test_check_alerts_below_and_only_once(db_session: AsyncSession) -> None:
    repository = AlertRepository()
    service = AlertService(repository)

    instrument = Instrument(
        code=f"ALERT_{uuid4().hex[:8]}",
        name="Alert Below Test",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    user = User(
        email=f"alert-below-{uuid4()}@example.com",
        password_hash="test-hash",
        role="user",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.flush()

    alert = await service.create_alert(
        db_session,
        user_id=user.id,
        instrument_id=instrument.id,
        direction="below",
        value=Decimal("35"),
    )

    triggered = await service.check_alerts(
        db_session,
        instrument_id=instrument.id,
        current_rate=Decimal("34"),
    )

    await db_session.flush()

    assert len(triggered) == 1
    assert alert.status == "triggered"
    assert alert.triggered_at is not None

    triggered_again = await service.check_alerts(
        db_session,
        instrument_id=instrument.id,
        current_rate=Decimal("30"),
    )

    assert triggered_again == []