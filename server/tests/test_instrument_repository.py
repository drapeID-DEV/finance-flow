from finance_flow.database import async_session_factory
from finance_flow.models.instrument import Instrument
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.services.instrument_service import InstrumentService


async def test_create_and_get_instrument() -> None:
    repository = InstrumentRepository()
    service = InstrumentService(repository)

    async with async_session_factory() as session:
        instrument = Instrument(
            code="TEST",
            name="Test Currency",
            type="currency",
            is_active=True,
        )

        created = await service.create(session, instrument)
        await session.commit()

        found = await service.get_by_code(session, "TEST")

        assert created.code == "TEST"
        assert found is not None
        assert found.name == "Test Currency"