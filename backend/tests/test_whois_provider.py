import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from app.services.providers.whois_provider import WHOISProvider
from app.config.settings import settings

@pytest.fixture
def whois_provider():
    settings.WHOIS_ENABLED = True
    return WHOISProvider()

@pytest.mark.asyncio
async def test_whois_disabled():
    settings.WHOIS_ENABLED = False
    provider = WHOISProvider()
    result = await provider.analyze_url("http://example.com")
    assert not result.is_successful
    assert "Disabled" in result.error_message

@pytest.mark.asyncio
@patch("app.services.providers.whois_provider.whois.whois")
async def test_whois_new_domain(mock_whois, whois_provider):
    # Simulate a domain registered yesterday
    mock_dict = {
        "creation_date": datetime.now(timezone.utc) - timedelta(days=1),
        "expiration_date": datetime.now(timezone.utc) + timedelta(days=364)
    }
    # whois.whois returns an object that acts like a dict
    mock_whois.return_value = mock_dict
    
    result = await whois_provider.analyze_url("http://new-phishing-site.com")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "Very New Domain" in result.indicators[0]["indicator"]
    assert result.indicators[0]["severity"] == "high"
    assert result.indicators[0]["evidence_category"] == "infrastructure"

@pytest.mark.asyncio
@patch("app.services.providers.whois_provider.whois.whois")
async def test_whois_old_domain(mock_whois, whois_provider):
    # Simulate a 10 year old domain
    mock_dict = {
        "creation_date": datetime.now(timezone.utc) - timedelta(days=3650),
        "expiration_date": datetime.now(timezone.utc) + timedelta(days=365)
    }
    mock_whois.return_value = mock_dict
    
    result = await whois_provider.analyze_url("http://google.com")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "Long Established Domain" in result.indicators[0]["indicator"]
    assert result.indicators[0]["severity"] == "low"
    assert result.indicators[0]["evidence_category"] == "trust"

@pytest.mark.asyncio
@patch("app.services.providers.whois_provider.whois.whois")
async def test_whois_timeout(mock_whois, whois_provider):
    def slow_whois(*args, **kwargs):
        import time
        time.sleep(0.5)
        return {}
        
    whois_provider.timeout = 0.1
    whois_provider.max_retries = 0
    mock_whois.side_effect = slow_whois
    
    result = await whois_provider.analyze_url("http://example.com")
    
    assert not result.is_successful
    assert "Timeout" in result.error_message
