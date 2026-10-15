
import httpx
import pytest

from finance_flow.sources.nbu import NbuSource


@pytest.mark.asyncio
async def test_get_rates_raises_for_server_error() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(500)
    )

    async with httpx.AsyncClient(transport=transport) as client:
        source = NbuSource(client)

        with pytest.raises(httpx.HTTPStatusError):
            await source.get_rates("20261001")


@pytest.mark.asyncio
async def test_get_rates_raises_for_bad_response_json() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json=[{"invalid": "data"}],
        )
    )

    async with httpx.AsyncClient(transport=transport) as client:
        source = NbuSource(client)

        with pytest.raises(ValueError):
            await source.get_rates("20261001")


@pytest.mark.asyncio
async def test_get_rates_returns_empty_for_empty_response() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=[])
    )

    async with httpx.AsyncClient(transport=transport) as client:
        source = NbuSource(client)

        rates = await source.get_rates("20261001")

    assert rates == []
