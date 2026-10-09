import asyncio
import os
import sys
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

# Force all tests to use the dedicated test database.
os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://finance_flow:finance_flow_dev"
    "@localhost:5433/finance_flow_test"
)

from finance_flow.config import get_settings  # noqa: E402

get_settings.cache_clear()

database_url = make_url(get_settings().database_url)
if database_url.database != "finance_flow_test":
    raise RuntimeError(
        "Unsafe test configuration: expected finance_flow_test, "
        f"got {database_url.database!r}"
    )

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest_asyncio.fixture
async def test_engine():
    from finance_flow.config import get_settings

    engine = create_async_engine(
        get_settings().database_url,
        echo=False,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    test_engine,
) -> AsyncGenerator[AsyncSession, None]:
    """Give each test a transaction that is rolled back after the test."""
    connection = await test_engine.connect()
    outer_transaction = await connection.begin()

    session_maker = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        async with session_maker() as session:
            yield session
    finally:
        if outer_transaction.is_active:
            await outer_transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    from finance_flow.dependencies import get_db_session
    from finance_flow.main import app

    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db_session, None)
