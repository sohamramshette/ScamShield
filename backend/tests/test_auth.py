def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "securepassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_existing_user(client):
    # Try registering the same user again
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "securepassword"},
    )
    assert response.status_code == 400


def test_login_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "securepassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
