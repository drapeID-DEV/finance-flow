
import argparse
import asyncio
import csv
import selectors
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.database import async_session_factory, engine
from finance_flow.models.instrument import Instrument
from finance_flow.models.rate import Rate


async def export_history(
    session: AsyncSession,
    code: str,
    from_date: date,
    to_date: date,
    output: Path,
) -> int:
    if from_date > to_date:
        raise ValueError("The start date must not be later than the end date.")

    statement = (
        select(
            Rate.date,
            Instrument.code,
            Instrument.name,
            Rate.rate,
            Rate.unit,
        )
        .join(Instrument, Rate.instrument_id == Instrument.id)
        .where(
            Instrument.code == code.upper(),
            Rate.date >= from_date,
            Rate.date <= to_date,
        )
        .order_by(Rate.date.asc())
    )

    result = await session.execute(statement)
    rows = result.all()

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["date", "code", "name", "rate", "unit"])

        for row in rows:
            writer.writerow(
                [
                    row.date.isoformat(),
                    row.code,
                    row.name,
                    str(row.rate),
                    row.unit,
                ]
            )

    return len(rows)


async def run_export(args: argparse.Namespace) -> int:
    try:
        async with async_session_factory() as session:
            count = await export_history(
                session=session,
                code=args.code,
                from_date=date.fromisoformat(args.from_date),
                to_date=date.fromisoformat(args.to_date),
                output=args.output,
            )

        print(
            f"Exported {count} rate records to: "
            f"{args.output.resolve()}"
        )
        return 0

    except ValueError as exc:
        print(f"Export error: {exc}", file=sys.stderr)
        return 1

    finally:
        await engine.dispose()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export FinanceFlow rate history to CSV."
    )
    parser.add_argument(
        "--code",
        required=True,
        help="Instrument code, for example USD or XAU.",
    )
    parser.add_argument(
        "--from",
        dest="from_date",
        required=True,
        help="Start date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--to",
        dest="to_date",
        required=True,
        help="End date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("rate_history.csv"),
        help="Output CSV path (default: rate_history.csv).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        if sys.platform == "win32":
            exit_code = asyncio.run(
                run_export(args),
                loop_factory=lambda: asyncio.SelectorEventLoop(
                    selectors.SelectSelector()
                ),
            )
        else:
            exit_code = asyncio.run(run_export(args))
    except (OSError, ValueError) as exc:
        print(f"Export error: {exc}", file=sys.stderr)
        exit_code = 1

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
