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

    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login-test@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401