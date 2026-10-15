
import csv
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.export_history import export_history
from finance_flow.models.instrument import Instrument
from finance_flow.models.rate import Rate


@pytest.mark.asyncio
async def test_export_history_writes_csv(
    db_session: AsyncSession,
    tmp_path,
) -> None:
    instrument = Instrument(
        code="EXPTEST",
        name="Export Test Instrument",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    db_session.add_all(
        [
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 10, 1),
                rate=Decimal("41.25000000"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 10, 2),
                rate=Decimal("42.50000000"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
        ]
    )
    await db_session.flush()

    output = tmp_path / "exports" / "history.csv"

    count = await export_history(
        session=db_session,
        code="exptest",
        from_date=date(2026, 10, 1),
        to_date=date(2026, 10, 2),
        output=output,
    )

    assert count == 2
    assert output.exists()

    with output.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 2
    assert rows[0] == {
        "date": "2026-10-01",
        "code": "EXPTEST",
        "name": "Export Test Instrument",
        "rate": "41.25000000",
        "unit": "1",
    }
    assert rows[1]["date"] == "2026-10-02"
    assert rows[1]["rate"] == "42.50000000"


@pytest.mark.asyncio
async def test_export_history_filters_date_range(
    db_session: AsyncSession,
    tmp_path,
) -> None:
    instrument = Instrument(
        code="EXPFILTER",
        name="Export Filter Test",
        type="currency",
        is_active=True,
    )
    db_session.add(instrument)
    await db_session.flush()

    db_session.add_all(
        [
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 9, 30),
                rate=Decimal("40"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 10, 1),
                rate=Decimal("41"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
            Rate(
                instrument_id=instrument.id,
                date=date(2026, 10, 3),
                rate=Decimal("43"),
                unit=1,
                created_at=datetime.now(UTC),
            ),
        ]
    )
    await db_session.flush()

    output = tmp_path / "filtered.csv"

    count = await export_history(
        session=db_session,
        code="EXPFILTER",
        from_date=date(2026, 10, 1),
        to_date=date(2026, 10, 2),
        output=output,
    )

    assert count == 1

    with output.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert [row["date"] for row in rows] == ["2026-10-01"]


@pytest.mark.asyncio
async def test_export_history_without_records_writes_header(
    db_session: AsyncSession,
    tmp_path,
) -> None:
    output = tmp_path / "empty.csv"

    count = await export_history(
        session=db_session,
        code="NO_SUCH_INSTRUMENT",
        from_date=date(2026, 10, 1),
        to_date=date(2026, 10, 2),
        output=output,
    )

    assert count == 0
    assert output.exists()

    with output.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        rows = list(csv.reader(csv_file))

    assert rows == [["date", "code", "name", "rate", "unit"]]


@pytest.mark.asyncio
async def test_export_history_rejects_invalid_date_range(
    db_session: AsyncSession,
    tmp_path,
) -> None:
    with pytest.raises(
        ValueError,
        match="start date must not be later",
    ):
        await export_history(
            session=db_session,
            code="USD",
            from_date=date(2026, 10, 10),
            to_date=date(2026, 10, 1),
            output=tmp_path / "invalid.csv",
        )
