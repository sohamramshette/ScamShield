import pytest
from app.services.ai_service import generate_explanation
import app.config.settings as settings

@pytest.mark.asyncio
async def test_generate_explanation_mock_mode():
    explanation, recommendation = await generate_explanation("website", "http://test.com", 65, [{"indicator": "Phishing", "severity": "high"}])
    assert explanation
    assert "Immediate Action Required" in recommendation

@pytest.mark.asyncio
async def test_generate_explanation_mock_safe():
    explanation, recommendation = await generate_explanation("website", "http://safe.com", 15, [])
    assert explanation
    assert "Appears Safe" in recommendation

@pytest.mark.asyncio
async def test_generate_explanation_production_no_key(monkeypatch):
    monkeypatch.setattr(settings.settings, "AI_MODE", "production")
    monkeypatch.setattr(settings.settings, "IBM_API_KEY", "")
    
    explanation, recommendation = await generate_explanation("website", "http://prod.com", 50, [])
    assert "Explanation unavailable" in explanation
    assert "Default to highest caution." in recommendation
