from fastapi import FastAPI

from finance_flow.api.alerts import router as alerts_router
from finance_flow.api.auth import router as auth_router
from finance_flow.api.collection import router as collection_router
from finance_flow.api.instruments import router as instruments_router
from finance_flow.api.portfolio import router as portfolio_router

app = FastAPI(
    title="FinanceFlow API",
    version="0.1.0",
)

app.include_router(instruments_router)
app.include_router(collection_router)
app.include_router(auth_router)
app.include_router(portfolio_router)
app.include_router(alerts_router)