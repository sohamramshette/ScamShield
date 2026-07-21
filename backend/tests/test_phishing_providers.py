import pytest
from unittest.mock import patch, MagicMock
from app.services.providers.phishtank import PhishTankProvider
from app.services.providers.urlscan import URLScanProvider
from app.services.providers.abuseipdb import AbuseIPDBProvider
from app.services.providers.registry import ProviderRegistry
from app.config.settings import settings

@pytest.fixture
def phishtank_provider():
    settings.PHISHTANK_ENABLED = True
    return PhishTankProvider()

@pytest.fixture
def urlscan_provider():
    settings.URLSCAN_ENABLED = True
    settings.URLSCAN_API_KEY = "test_key"
    return URLScanProvider()

@pytest.fixture
def abuseipdb_provider():
    settings.ABUSEIPDB_ENABLED = True
    settings.ABUSEIPDB_API_KEY = "test_key"
    return AbuseIPDBProvider()

@pytest.mark.asyncio
async def test_registry():
    settings.PHISHTANK_ENABLED = True
    settings.URLSCAN_ENABLED = True
    settings.URLSCAN_API_KEY = "dummy"
    settings.ABUSEIPDB_ENABLED = False
    
    providers = ProviderRegistry.get_enabled_providers()
    
    names = [p.provider_name() for p in providers]
    assert "phishtank" in names
    assert "urlscan" in names
    assert "abuseipdb" not in names
    assert "offline_rule_engine" in names

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_phishtank_verified(mock_post, phishtank_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": {
            "in_database": True,
            "valid": True
        }
    }
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp
    
    result = await phishtank_provider.analyze_url("http://phishing.com")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "Verified Phishing" in result.indicators[0]["indicator"]
    assert result.indicators[0]["severity"] == "critical"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_urlscan_malicious(mock_get, urlscan_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "verdicts": {
                    "overall": {"malicious": True}
                }
            }
        ]
    }
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp
    
    result = await urlscan_provider.analyze_url("http://phishing.com")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "URLScan: Malicious Activity" in result.indicators[0]["indicator"]

@pytest.mark.asyncio
@patch("app.services.providers.abuseipdb.asyncio.to_thread")
@patch("httpx.AsyncClient.get")
async def test_abuseipdb_high_score(mock_get, mock_to_thread, abuseipdb_provider):
    mock_to_thread.return_value = "192.168.1.1" # Mock DNS
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "abuseConfidenceScore": 85
        }
    }
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp
    
    result = await abuseipdb_provider.analyze_url("http://phishing.com")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "High Abuse Score" in result.indicators[0]["indicator"]
    assert result.indicators[0]["severity"] == "critical"
