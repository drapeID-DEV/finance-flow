from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from finance_flow.models.instrument import Instrument
from finance_flow.repositories.instrument_repository import InstrumentRepository
from finance_flow.services.instrument_service import InstrumentService


async def test_create_and_get_instrument() -> None:
    engine = create_async_engine(
        "postgresql+psycopg://finance_flow:finance_flow_dev"
        "@localhost:5433/finance_flow",
    )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    repository = InstrumentRepository()
    service = InstrumentService(repository)

    async with session_factory() as session:
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

    await engine.dispose()