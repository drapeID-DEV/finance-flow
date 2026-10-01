from dataclasses import dataclass
from decimal import Decimal

import httpx

from finance_flow.config import get_settings


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
        url = f"{self.base_url}/exchange"

        response = await self.client.get(
            url,
            params={
                "json": True,
                "date": date,
            },
        )
        response.raise_for_status()

        data = response.json()

        return [
            NbuRate(
                code=item["cc"],
                name=item["txt"],
                rate=Decimal(str(item["rate"])),
                unit=item["r030"],
            )
            for item in data
        ]