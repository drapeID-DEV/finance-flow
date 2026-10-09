from fastapi.testclient import TestClient

from finance_flow.main import app

client = TestClient(app)


def test_register() -> None:
    response = client.post(
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


def test_login() -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "login-test@example.com",
            "password": "test-password",
        },
    )

    assert register_response.status_code in (201, 409)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login-test@example.com",
            "password": "test-password",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"

    assert response.cookies["access_token"]
    assert response.cookies["refresh_token"]

    refresh_token = response.cookies["refresh_token"]

    from sqlalchemy import select

    from finance_flow.auth import hash_refresh_token
    from finance_flow.database import async_session_factory
    from finance_flow.models.refresh_token import RefreshToken

    async def check_refresh_token() -> None:
        async with async_session_factory() as session:
            result = await session.execute(
                select(RefreshToken).where(
                    RefreshToken.token_hash
                    == hash_refresh_token(refresh_token)
                )
            )
            token_record = result.scalar_one_or_none()

            assert token_record is not None
            assert token_record.token_hash != refresh_token

    import asyncio

    asyncio.run(check_refresh_token())


def test_login_with_wrong_password() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login-test@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_logout() -> None:
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"


def test_auth_with_cookie() -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "cookie-test@example.com",
            "password": "test-password",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "cookie-test@example.com",
            "password": "test-password",
        },
    )

    assert login_response.status_code == 200
    assert "access_token" in client.cookies

    me_response = client.get("/api/v1/auth/me")

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "cookie-test@example.com"


def test_refresh_rotates_tokens() -> None:
    email = "refresh-test@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "test-password",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "test-password",
        },
    )

    assert login_response.status_code == 200

    old_refresh_token = client.cookies["refresh_token"]
    old_access_token = client.cookies["access_token"]

    refresh_response = client.post("/api/v1/auth/refresh")

    assert refresh_response.status_code == 200
    assert (
        refresh_response.json()["message"]
        == "Tokens refreshed successfully"
    )

    new_refresh_token = client.cookies["refresh_token"]
    new_access_token = client.cookies["access_token"]

    assert new_refresh_token != old_refresh_token
    assert new_access_token != old_access_token

    import asyncio

    from sqlalchemy import select

    from finance_flow.auth import hash_refresh_token
    from finance_flow.database import async_session_factory
    from finance_flow.models.refresh_token import RefreshToken

    async def check_rotation() -> None:
        async with async_session_factory() as session:
            old_result = await session.execute(
                select(RefreshToken).where(
                    RefreshToken.token_hash
                    == hash_refresh_token(old_refresh_token)
                )
            )
            assert old_result.scalar_one_or_none() is None

            new_result = await session.execute(
                select(RefreshToken).where(
                    RefreshToken.token_hash
                    == hash_refresh_token(new_refresh_token)
                )
            )
            assert new_result.scalar_one_or_none() is not None

    asyncio.run(check_rotation())


def test_old_refresh_token_cannot_be_reused() -> None:
    client.cookies.clear()

    email = "refresh-reuse-test@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "test-password",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "test-password",
        },
    )
    assert login_response.status_code == 200

    old_refresh_token = client.cookies["refresh_token"]

    refresh_response = client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200

    client.cookies.set(
        "refresh_token",
        old_refresh_token,
        path="/api/v1/auth",
    )
    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


def test_logout_revokes_refresh_token() -> None:
    client.cookies.clear()

    email = "logout-revoke-test@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "test-password",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "test-password",
        },
    )
    assert login_response.status_code == 200

    refresh_token = client.cookies.get(
        "refresh_token",
        path="/api/v1/auth",
    )

    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200

    client.cookies.set(
        "refresh_token",
        refresh_token,
        path="/api/v1/auth",
    )

    refresh_response = client.post("/api/v1/auth/refresh")

    assert refresh_response.status_code == 401