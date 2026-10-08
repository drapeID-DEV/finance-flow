from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from finance_flow.models.base import Base
from finance_flow.models.instrument import Instrument


class Rate(Base):
    __tablename__ = "rates"

    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "date",
            name="uq_rates_instrument_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id"),
        nullable=False,
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    rate: Mapped[Decimal] = mapped_column(
        Numeric(18, 8),
        nullable=False,
    )

    unit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    instrument: Mapped[Instrument] = relationship()