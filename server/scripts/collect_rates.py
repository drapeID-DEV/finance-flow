
import asyncio
import logging
from datetime import date

from finance_flow.database import engine
from finance_flow.services.collection_runner import run_collection


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


async def main() -> None:
    rate_date = date.today()

    try:
        logging.info("Starting NBU collection for %s", rate_date)

        saved_count = await run_collection(rate_date)

        logging.info(
            "NBU collection completed for %s. Saved rates: %s",
            rate_date,
            saved_count,
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
