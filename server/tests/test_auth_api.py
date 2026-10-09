import pytest
from httpx import AsyncClient
from sqlalchemy import select

from finance_flow.auth import hash_refresh_token
from finance_flow.models.refresh_token import RefreshToken


@pytest.mark.asyncio
async def test_register(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "api-test@example.com",
            "password": "test-password",
        },
    )

    assert response.status_code in (201, 409)

    if response.status_code == 201:
        data = response.json()
        assert data["email"] == "api-test@example.com"
        assert data["role"] == "user"
        assert "password_hash" not in data


@pytest.mark.asyncio
async def test_login(client: AsyncClient, db_session) -> None:
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login-test@example.com",
            "password": "test-password",
        },
    )
    assert register_response.status_code in (201, 409)

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login-test@example.com",
            "password": "test-password",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"

    refresh_token = response.cookies["refresh_token"]

    result = await db_session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(refresh_token)
        )
    )
    token_record = result.scalar_one_or_none()

    assert token_record is not None
    assert token_record.token_hash != refresh_token


@pytest.mark.asyncio
async def test_login_with_wrong_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login-test@example.com",
            "password": "wrong-password",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"


@pytest.mark.asyncio
async def test_auth_with_cookie(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "cookie-test@example.com",
            "password": "test-password",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "cookie-test@example.com",
            "password": "test-password",
        },
    )

    assert login_response.status_code == 200
    assert "access_token" in client.cookies

    me_response = await client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "cookie-test@example.com"


@pytest.mark.asyncio
async def test_refresh_rotates_tokens(
    client: AsyncClient,
    db_session,
) -> None:
    email = "refresh-test@example.com"

    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "test-password"},
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "test-password"},
    )
    assert login_response.status_code == 200

    old_refresh_token = client.cookies["refresh_token"]
    old_access_token = client.cookies["access_token"]

    refresh_response = await client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200
    assert (
        refresh_response.json()["message"]
        == "Tokens refreshed successfully"
    )

    new_refresh_token = client.cookies["refresh_token"]
    new_access_token = client.cookies["access_token"]

    assert new_refresh_token != old_refresh_token
    assert new_access_token != old_access_token

    old_result = await db_session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(old_refresh_token)
        )
    )
    assert old_result.scalar_one_or_none() is None

    new_result = await db_session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(new_refresh_token)
        )
    )
    assert new_result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_old_refresh_token_cannot_be_reused(
    client: AsyncClient,
) -> None:
    client.cookies.clear()
    email = "refresh-reuse-test@example.com"

    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "test-password"},
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "test-password"},
    )
    assert login_response.status_code == 200

    old_refresh_token = client.cookies["refresh_token"]

    refresh_response = await client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200

    client.cookies.set(
        "refresh_token",
        old_refresh_token,
        path="/api/v1/auth",
    )
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(
    client: AsyncClient,
) -> None:
    client.cookies.clear()
    email = "logout-revoke-test@example.com"

    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "test-password"},
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "test-password"},
    )
    assert login_response.status_code == 200

    refresh_token = client.cookies.get(
        "refresh_token",
        path="/api/v1/auth",
    )

    logout_response = await client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200

    client.cookies.set(
        "refresh_token",
        refresh_token,
        path="/api/v1/auth",
    )

    refresh_response = await client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 401
