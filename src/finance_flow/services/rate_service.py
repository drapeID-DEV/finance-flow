from collections import defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.rate import Rate
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.sources.nbu import NbuRate


class RateService:
    def __init__(
        self,
        rate_repository: RateRepository,
        instrument_repository: InstrumentRepository,
    ) -> None:
        self.rate_repository = rate_repository
        self.instrument_repository = instrument_repository

    async def save_rate(
        self,
        session: AsyncSession,
        nbu_rate: NbuRate,
        rate_date: date,
    ) -> Rate | None:
        instrument = await self.instrument_repository.get_by_code(
            session,
            nbu_rate.code,
        )

        if instrument is None:
            return None

        existing = await self.rate_repository.get_by_instrument_and_date(
            session,
            instrument.id,
            rate_date,
        )

        if existing is not None:
            return None

        rate = Rate(
            instrument_id=instrument.id,
            date=rate_date,
            rate=Decimal(nbu_rate.rate),
            unit=nbu_rate.unit,
            created_at=datetime.now(UTC),
        )

        return await self.rate_repository.add(session, rate)

    async def get_history(
        self,
        session: AsyncSession,
        instrument_code: str,
        from_date: date,
        to_date: date,
    ) -> list[Rate]:
        instrument = await self.instrument_repository.get_by_code(
            session,
            instrument_code,
        )

        if instrument is None:
            return []

        return await self.rate_repository.get_history(
            session,
            instrument.id,
            from_date,
            to_date,
        )

    async def get_aggregated_history(
        self,
        session: AsyncSession,
        instrument_code: str,
        from_date: date,
        to_date: date,
        aggregation: str,
        page: int = 1,
        page_size: int = 30,
    ) -> list[dict[str, object]]:
        rates = await self.get_history(
            session,
            instrument_code,
            from_date,
            to_date,
        )

        if aggregation == "day":
            return [
                {
                    "date": rate.date,
                    "rate": rate.rate,
                    "unit": rate.unit,
                }
                for rate in rates
            ]

        groups: dict[str, list[Rate]] = defaultdict(list)

        for rate in rates:
            if aggregation == "week":
                iso = rate.date.isocalendar()
                key = f"{iso.year}-W{iso.week:02d}"
            else:
                key = f"{rate.date.year}-{rate.date.month:02d}"

            groups[key].append(rate)

        result: list[dict[str, object]] = []

        for period, period_rates in groups.items():
            values = [rate.rate for rate in period_rates]

            result.append(
                {
                    "period": period,
                    "open": values[0],
                    "close": values[-1],
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "unit": period_rates[0].unit,
                }
            )

        start = (page - 1) * page_size
        end = start + page_size

        return result[start:end]