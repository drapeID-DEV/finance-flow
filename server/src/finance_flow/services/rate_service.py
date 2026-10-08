from collections import defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.rate import Rate
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.repositories.rate_repository import RateRepository
from finance_flow.services.alert_service import AlertService
from finance_flow.sources.nbu import NbuRate


class RateService:
    def __init__(
        self,
        rate_repository: RateRepository,
        instrument_repository: InstrumentRepository,
        alert_service: AlertService,
    ) -> None:
        self.rate_repository = rate_repository
        self.instrument_repository = instrument_repository
        self.alert_service = alert_service

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

        saved_rate = await self.rate_repository.add(
            session,
            rate,
        )

        await self.alert_service.check_alerts(
            session,
            instrument_id=instrument.id,
            current_rate=rate.rate,
        )

        return saved_rate

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

    async def calculate_volatility(
        self,
        session: AsyncSession,
        instrument_code: str,
        from_date: date,
        to_date: date,
    ) -> Decimal:
        rates = await self.get_history(
            session,
            instrument_code,
            from_date,
            to_date,
        )

        if not rates:
            return Decimal("0")

        values = [rate.rate for rate in rates]

        return max(values) - min(values)

    async def compare_instruments(
        self,
        session: AsyncSession,
        first_code: str,
        second_code: str,
        from_date: date,
        to_date: date,
    ) -> list[dict[str, date | Decimal]]:
        first_instrument = await self.instrument_repository.get_by_code(
            session,
            first_code,
        )
        second_instrument = await self.instrument_repository.get_by_code(
            session,
            second_code,
        )

        if first_instrument is None or second_instrument is None:
            raise ValueError("Instrument not found")

        rates = await self.rate_repository.get_history_for_instruments(
            session,
            [first_instrument.id, second_instrument.id],
            from_date,
            to_date,
        )

        first_rates: dict[date, Decimal] = {}
        second_rates: dict[date, Decimal] = {}

        for rate in rates:
            if rate.instrument_id == first_instrument.id:
                first_rates[rate.date] = rate.rate
            elif rate.instrument_id == second_instrument.id:
                second_rates[rate.date] = rate.rate

        common_dates = sorted(set(first_rates) & set(second_rates))

        return [
            {
                "date": rate_date,
                "first_rate": first_rates[rate_date],
                "second_rate": second_rates[rate_date],
            }
            for rate_date in common_dates
        ]

    async def find_significant_changes(
        self,
        session: AsyncSession,
        instrument_code: str,
        from_date: date,
        to_date: date,
        threshold: Decimal,
    ) -> list[dict[str, date | Decimal]]:
        if threshold <= 0:
            raise ValueError("Threshold must be greater than zero")

        rates = await self.get_history(
            session,
            instrument_code,
            from_date,
            to_date,
        )

        result: list[dict[str, date | Decimal]] = []

        for previous, current in zip(rates, rates[1:], strict=False):
            if previous.rate == 0:
                continue

            change = abs(current.rate - previous.rate) / previous.rate

            if change > threshold:
                result.append(
                    {
                        "date": current.date,
                        "rate": current.rate,
                        "change": change,
                    }
                )

        return result