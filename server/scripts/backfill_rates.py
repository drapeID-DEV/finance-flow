
import asyncio
from datetime import date, timedelta

from finance_flow.services.collection_runner import run_collection


async def main() -> None:
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    print(f"Loading NBU rates from {start_date} to {end_date}")

    current_date = start_date
    total_saved = 0

    while current_date <= end_date:
        print(f"Processing {current_date}...", flush=True)

        try:
            saved = await asyncio.wait_for(
                run_collection(current_date),
                timeout=60,
            )
            total_saved += saved
            print(f"{current_date}: saved {saved} rates", flush=True)
        except TimeoutError:
            print(
                f"{current_date}: timed out after 60 seconds",
                flush=True,
            )
        except Exception as exc:
            print(
                f"{current_date}: ERROR — {exc!r}",
                flush=True,
            )

        current_date += timedelta(days=1)

    print(f"Finished. Total saved rates: {total_saved}")


if __name__ == "__main__":
    import selectors

    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )