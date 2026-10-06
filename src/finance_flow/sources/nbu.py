from dataclasses import dataclass
from decimal import Decimal

import httpx
from pydantic import BaseModel

from finance_flow.config import get_settings


class NbuRateResponse(BaseModel):
    r030: int
    txt: str
    rate: Decimal
    cc: str


@dataclass(frozen=True, slots=True)
class NbuRate:
    code: str
    name: str
    rate: Decimal
    unit: int


class NbuSource:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.base_url = get_settings().nbu_base_url
        self.client = client

    async def get_rates(self, date: str) -> list[NbuRate]:
        url = f"{self.base_url}/statdirectory/exchangenew"

        response = await self.client.get(
            url,
            params={
                "json": True,
                "date": date,
            },
        )
        
        if response.status_code == 404:
            return []

        response.raise_for_status()

        data = [NbuRateResponse.model_validate(item) for item in response.json()]

        return [
            NbuRate(
                code=item.cc,
                name=item.txt,
                rate=item.rate,
                unit=1,
            )
            for item in data
        ]