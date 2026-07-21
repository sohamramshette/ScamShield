import pytest
import uuid
from app.schemas.all_schemas import Token
from unittest.mock import AsyncMock, patch
from app.schemas.all_schemas import ThreatIndicatorSchema

def test_scan_website_unauthorized(client):
    response = client.post("/api/v1/scanners/website", json={"target": "http://example.com"})
    assert response.status_code == 401

def get_auth_token(client):
    unique_email = f"scanner_{uuid.uuid4().hex[:6]}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "password123"},
    )
    login_response = client.post("/api/v1/auth/login", data={"username": unique_email, "password": "password123"})
    return login_response.json()["access_token"]

@patch("app.api.v1.scanners.get_orchestrator")
@patch("app.api.v1.scanners.EvidenceEngine.process_evidence")
def test_scan_website_authorized(mock_process, mock_get_orch, client):
    mock_orch = AsyncMock()
    mock_orch.analyze.return_value = {"mock_provider": {"success": True}}
    mock_get_orch.return_value = mock_orch
    
    mock_process.return_value = [
        ThreatIndicatorSchema(indicator="Test", severity="medium", category="threat")
    ]
    
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/scanners/website", json={"target": "http://example.com"}, headers=headers)
    assert response.status_code == 200
    assert "risk_score" in response.json()

@patch("app.api.v1.scanners.get_orchestrator")
@patch("app.api.v1.scanners.EvidenceEngine.process_evidence")
def test_scan_qr_authorized(mock_process, mock_get_orch, client):
    mock_orch = AsyncMock()
    mock_orch.analyze.return_value = {"mock_provider": {"success": True}}
    mock_get_orch.return_value = mock_orch
    
    mock_process.return_value = [
        ThreatIndicatorSchema(indicator="Test", severity="low", category="threat")
    ]
    
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/scanners/qr", json={"target": "http://example-qr.com"}, headers=headers)
    assert response.status_code == 200
    assert "risk_score" in response.json()

@patch("app.api.v1.scanners.get_orchestrator")
@patch("app.api.v1.scanners.EvidenceEngine.process_evidence")
def test_scan_upi_authorized(mock_process, mock_get_orch, client):
    mock_orch = AsyncMock()
    mock_orch.analyze.return_value = {"mock_provider": {"success": True}}
    mock_get_orch.return_value = mock_orch
    
    mock_process.return_value = [
        ThreatIndicatorSchema(indicator="Test", severity="high", category="threat")
    ]
    
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/scanners/upi", json={"target": "test@upi"}, headers=headers)
    assert response.status_code == 200
    assert "risk_score" in response.json()
