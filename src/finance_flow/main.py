from fastapi import FastAPI

from finance_flow.api.instruments import router as instruments_router


app = FastAPI(
    title="FinanceFlow API",
    version="0.1.0",
)

app.include_router(instruments_router)