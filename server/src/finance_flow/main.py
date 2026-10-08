from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from finance_flow.api.alerts import router as alerts_router
from finance_flow.api.auth import router as auth_router
from finance_flow.api.collection import router as collection_router
from finance_flow.api.instruments import router as instruments_router
from finance_flow.api.portfolio import router as portfolio_router

app = FastAPI(
    title="FinanceFlow API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(instruments_router)
app.include_router(collection_router)
app.include_router(auth_router)
app.include_router(portfolio_router)
app.include_router(alerts_router)