from decimal import Decimal

import httpx

from finance_flow.sources.nbu import NbuSource


async def test_get_rates() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json=[
                {
                    "r030": 840,
                    "txt": "Долар США",
                    "rate": 41.25,
                    "cc": "USD",
                },
                {
                    "r030": 978,
                    "txt": "Євро",
                    "rate": 48.55,
                    "cc": "EUR",
                },
                {
                    "r030": 392,
                    "txt": "Єна",
                    "rate": 0.27,
                    "cc": "JPY",
                },
            ],
        ),
    )

    async with httpx.AsyncClient(transport=transport) as client:
        source = NbuSource(client)

        rates = await source.get_rates("01.10.2026")

    assert len(rates) == 3

    assert rates[0].code == "USD"
    assert rates[0].rate == Decimal("41.25")
    assert rates[0].unit == 840

    assert rates[1].code == "EUR"
    assert rates[1].rate == Decimal("48.55")
    assert rates[1].unit == 978

    assert rates[2].code == "JPY"
    assert rates[2].rate == Decimal("0.27")
    assert rates[2].unit == 392