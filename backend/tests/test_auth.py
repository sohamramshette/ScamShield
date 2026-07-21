import pytest
import uuid

def test_register_user(client):
    email = f"test_{uuid.uuid4()}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data


def test_register_existing_user(client):
    email = f"test_{uuid.uuid4()}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword"},
    )
    # Try registering the same user again
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword"},
    )
    assert response.status_code == 400


def test_login_user(client):
    email = f"test_{uuid.uuid4()}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "securepassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    email = f"test_{uuid.uuid4()}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
