
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from finance_flow.api.alerts import router as alerts_router
from finance_flow.api.auth import router as auth_router
from finance_flow.api.collection import router as collection_router
from finance_flow.api.dashboard import router as dashboard_router
from finance_flow.api.instruments import router as instruments_router
from finance_flow.api.portfolio import router as portfolio_router
from finance_flow.config import get_settings
from finance_flow.database import engine
from finance_flow.scheduler import scheduler, start_scheduler, stop_scheduler

settings = get_settings()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    start_scheduler()

    print("Scheduler running:", scheduler.running)
    print("Scheduled jobs:", scheduler.get_jobs())

    try:
        yield
    finally:
        stop_scheduler()
        await engine.dispose()


app = FastAPI(
    title="FinanceFlow API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(instruments_router)
app.include_router(collection_router)
app.include_router(auth_router)
app.include_router(portfolio_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
