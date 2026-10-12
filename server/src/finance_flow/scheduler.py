
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from finance_flow.services.collection_runner import run_collection

logger = logging.getLogger(__name__)

KYIV_TIMEZONE = ZoneInfo("Europe/Kyiv")

scheduler = AsyncIOScheduler(timezone=KYIV_TIMEZONE)


async def scheduled_collection() -> None:
    rate_date = datetime.now(KYIV_TIMEZONE).date()

    try:
        saved_count = await run_collection(rate_date)
        logger.info(
            "Scheduled collection completed for %s. Saved rates: %s",
            rate_date,
            saved_count,
        )
    except Exception:
        logger.exception(
            "Scheduled collection failed for %s",
            rate_date,
        )


def start_scheduler() -> None:
    if scheduler.running:
        return

    scheduler.add_job(
        scheduled_collection,
        trigger="cron",
        hour=9,
        minute=0,
        id="daily_nbu_collection",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )

    scheduler.start()
    logger.info("Daily NBU collection scheduled for 09:00 Europe/Kyiv")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("NBU collection scheduler stopped")
