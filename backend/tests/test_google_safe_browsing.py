import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.providers.google_safe_browsing import GoogleSafeBrowsingProvider
from app.services.evidence_engine import EvidenceEngine
from app.services.providers.base import ProviderResult
from app.config.settings import settings

@pytest.fixture
def gsb_provider():
    settings.GSB_ENABLED = True
    settings.GSB_API_KEY = "test_key"
    return GoogleSafeBrowsingProvider()

@pytest.mark.asyncio
async def test_missing_api_key():
    settings.GSB_API_KEY = ""
    provider = GoogleSafeBrowsingProvider()
    result = await provider.analyze_url("http://example.com")
    assert not result.is_successful
    assert "Missing API Key" in result.error_message

@pytest.mark.asyncio
async def test_gsb_disabled():
    settings.GSB_ENABLED = False
    provider = GoogleSafeBrowsingProvider()
    result = await provider.analyze_url("http://example.com")
    assert not result.is_successful
    assert "Provider Disabled" in result.error_message

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_valid_response(mock_post, gsb_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "matches": [
            {
                "threatType": "MALWARE",
                "platformType": "ANY_PLATFORM",
                "threatEntryType": "URL",
                "threat": {"url": "http://malware.testing.google.test/testing/mac"}
            }
        ]
    }
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    result = await gsb_provider.analyze_url("http://malware.testing.google.test/testing/mac")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert result.indicators[0]["severity"] == "critical"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_rate_limited(mock_post, gsb_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    
    with patch("asyncio.sleep", new_callable=AsyncMock):
        mock_post.side_effect = httpx.HTTPStatusError("Rate Limited", request=MagicMock(), response=mock_resp)
        result = await gsb_provider.analyze_url("http://example.com")
        
        assert not result.is_successful
        assert "Rate Limited" in result.error_message

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_timeout_fallback(mock_post, gsb_provider):
    with patch("asyncio.sleep", new_callable=AsyncMock):
        mock_post.side_effect = httpx.TimeoutException("Timeout")
        result = await gsb_provider.analyze_url("http://example.com")
        
        assert not result.is_successful
        assert "Timeout" in result.error_message

def test_evidence_engine_aggregation():
    # Simulate a scenario where Offline says medium, VT says critical, GSB says critical
    res1 = ProviderResult(
        provider_name="offline_rule_engine",
        trust_weight=0.45,
        is_successful=True,
        indicators=[{"indicator": "suspicious domain", "severity": "medium", "description": "Offline finding"}]
    )
    res2 = ProviderResult(
        provider_name="virustotal",
        trust_weight=1.00,
        is_successful=True,
        indicators=[{"indicator": "Malware detected", "severity": "critical", "description": "VT engines flagged"}]
    )
    res3 = ProviderResult(
        provider_name="google_safe_browsing",
        trust_weight=1.00,
        is_successful=True,
        indicators=[{"indicator": "Google Safe Browsing: Malware", "severity": "critical", "description": "GSB flagged"}]
    )
    
    final_indicators = EvidenceEngine.process_evidence([res1, res2, res3])
    
    # We should have grouped the Malware ones into a single indicator
    # And the Suspicious one as a separate indicator
    assert len(final_indicators) == 2
    
    malware_ind = next((i for i in final_indicators if "Malware" in i.indicator), None)
    suspicious_ind = next((i for i in final_indicators if "Suspicious" in i.indicator), None)
    
    assert malware_ind is not None
    assert malware_ind.severity == "critical"
    assert "virustotal" in malware_ind.indicator
    assert "google_safe_browsing" in malware_ind.indicator
    
    assert suspicious_ind is not None
    assert suspicious_ind.severity == "medium"
    assert "offline_rule_engine" in suspicious_ind.indicator
