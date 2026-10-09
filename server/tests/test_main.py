import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_application_starts(client: AsyncClient) -> None:
    response = await client.get("/docs")
    assert response.status_code == 200
