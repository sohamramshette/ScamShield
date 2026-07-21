import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_dashboard_stats(db_session, auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/dashboard/stats", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "risk_distribution" in data
    assert "provider_health" in data
    assert "recent_activity" in data
    assert "system_health" in data
