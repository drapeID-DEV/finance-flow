
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_instruments_requires_authentication(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/instruments/admin/all")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_collection_requires_authentication(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/collect/run",
        params={"date": "2026-10-01"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_regular_user_cannot_access_admin_instruments(
    client: AsyncClient,
) -> None:
    email = f"regular-{uuid4().hex}@example.com"
    password = "test-password-123"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    response = await client.get("/api/v1/instruments/admin/all")

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_regular_user_cannot_start_collection(
    client: AsyncClient,
) -> None:
    email = f"collector-{uuid4().hex}@example.com"
    password = "test-password-123"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    response = await client.post(
        "/api/v1/collect/run",
        params={"date": "2026-10-01"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"
