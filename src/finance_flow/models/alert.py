from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from finance_flow.models.base import Base
from finance_flow.models.instrument import Instrument
from finance_flow.models.user import User


class Alert(Base):
    __tablename__ = "alerts"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "instrument_id",
            "direction",
            "value",
            name="uq_alerts_user_instrument_direction_value",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id"),
        nullable=False,
    )

    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(18, 8),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[User] = relationship()
    instrument: Mapped[Instrument] = relationship()