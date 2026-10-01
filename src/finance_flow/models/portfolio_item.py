from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from finance_flow.models.base import Base
from finance_flow.models.instrument import Instrument
from finance_flow.models.portfolio import Portfolio


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    __table_args__ = (
        UniqueConstraint(
            "portfolio_id",
            "instrument_id",
            name="uq_portfolio_items_portfolio_instrument",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id"),
        nullable=False,
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id"),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 8),
        nullable=False,
        default=Decimal("1"),
    )

    portfolio: Mapped[Portfolio] = relationship()
    instrument: Mapped[Instrument] = relationship()