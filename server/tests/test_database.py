from sqlalchemy import text

from finance_flow.database import async_session_factory


async def test_database_connection() -> None:
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1