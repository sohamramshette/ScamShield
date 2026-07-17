import pytest
import uuid
from app.schemas.all_schemas import Token

def test_scan_website_unauthorized(client):
    response = client.post("/api/v1/scanners/website", json={"target": "http://example.com"})
    assert response.status_code == 401

def get_auth_token(client):
    unique_email = f"scanner_{uuid.uuid4().hex[:6]}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "password123"},
    )
    # Login to get token
    login_response = client.post("/api/v1/auth/login", data={"username": unique_email, "password": "password123"})
    return login_response.json()["access_token"]

def test_scan_website_authorized(client, monkeypatch):
    async def mock_analyze(*args, **kwargs):
        return [{"indicator": "mock", "severity": "low"}]
    
    import app.api.v1.scanners
    monkeypatch.setattr(app.api.v1.scanners, "analyze_url", mock_analyze)

    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/scanners/website", json={"target": "http://example.com"}, headers=headers)
    assert response.status_code == 200
    assert "risk_score" in response.json()

def test_scan_qr_authorized(client, monkeypatch):
    async def mock_analyze(*args, **kwargs):
        return [{"indicator": "mock", "severity": "low"}]
    import app.api.v1.scanners
    monkeypatch.setattr(app.api.v1.scanners, "analyze_url", mock_analyze)

    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/scanners/qr", json={"target": "http://example-qr.com"}, headers=headers)
    assert response.status_code == 200
    assert "risk_score" in response.json()

def test_scan_upi_authorized(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/scanners/upi", json={"target": "test@upi"}, headers=headers)
    assert response.status_code == 200
    assert "risk_score" in response.json()
