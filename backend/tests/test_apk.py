import pytest
from fastapi.testclient import TestClient
from main import app as fastapi_app
from app.api.v1.auth import get_current_user
from app.models.user import User
import os
import io

client = TestClient(fastapi_app)

def test_analyze_apk_endpoint_safe(monkeypatch):
    # Mock authentication
    fastapi_app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@scamshield.ai", is_active=True)
    
    class MockScan:
        id = "mock-scan-id-1"
        status = "completed"
    
    async def mock_analyze_apk(filepath, user_id, db, orchestrator):
        return MockScan()

    import app.api.v1.apk
    monkeypatch.setattr(app.api.v1.apk, "analyze_apk", mock_analyze_apk)

    # Test file upload
    file_content = b"fake apk content"
    files = {'file': ('safe.apk', file_content, 'application/vnd.android.package-archive')}
    
    response = client.post("/api/v1/apk/analyze", files=files)
    
    assert response.status_code == 200
    assert response.json()["id"] == "mock-scan-id-1"
    
    fastapi_app.dependency_overrides.clear()

def test_analyze_apk_endpoint_invalid_ext(monkeypatch):
    # Mock authentication
    fastapi_app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@scamshield.ai", is_active=True)
    
    # Test file upload with wrong extension
    file_content = b"fake apk content"
    files = {'file': ('safe.txt', file_content, 'text/plain')}
    
    response = client.post("/api/v1/apk/analyze", files=files)
    
    assert response.status_code == 400
    assert "Only APK files are supported" in response.text
    
    fastapi_app.dependency_overrides.clear()
