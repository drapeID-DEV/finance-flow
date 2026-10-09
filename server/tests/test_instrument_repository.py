import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.instrument import Instrument
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.services.instrument_service import InstrumentService


@pytest.mark.asyncio
async def test_create_and_get_instrument(db_session: AsyncSession) -> None:
    repository = InstrumentRepository()
    service = InstrumentService(repository)

    instrument = Instrument(
        code="TEST",
        name="Test Currency",
        type="currency",
        is_active=True,
    )

    created = await service.create(db_session, instrument)
    await db_session.flush()

    found = await service.get_by_code(db_session, "TEST")

    assert created.code == "TEST"
    assert found is not None
    assert found.name == "Test Currency"