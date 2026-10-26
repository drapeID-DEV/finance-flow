
import asyncio
import selectors

import httpx
from sqlalchemy import text

from finance_flow.database import async_session_factory, engine
from finance_flow.config import get_settings


async def main() -> None:
    settings = get_settings()

    # 1. Проверяем API НБУ
    print("Checking NBU API...", flush=True)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.nbu_base_url}/statdirectory/exchangenew",
                params={"json": True, "date": "20261015"},
            )
            response.raise_for_status()
            print(
                f"NBU OK: HTTP {response.status_code}, "
                f"received {len(response.json())} records",
                flush=True,
            )
    except Exception as exc:
        print(f"NBU ERROR: {type(exc).__name__}: {exc}", flush=True)

    # 2. Проверяем подключение к PostgreSQL
    print("Checking Neon PostgreSQL...", flush=True)
    try:
        async def check_db() -> None:
            async with async_session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                print(f"Database OK: {result.scalar_one()}", flush=True)

        await asyncio.wait_for(check_db(), timeout=15)
    except Exception as exc:
        print(
            f"DATABASE ERROR: {type(exc).__name__}: {exc}",
            flush=True,
        )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )
