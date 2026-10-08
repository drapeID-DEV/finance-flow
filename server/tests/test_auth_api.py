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

    data = response.json()

    assert response.status_code == 200
    assert data["message"] == "Login successful"

    assert "access_token" in response.cookies
    assert response.cookies["access_token"]


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