import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.providers.virustotal import VirusTotalProvider
from app.config.settings import settings

@pytest.fixture
def vt_provider():
    settings.VT_ENABLED = True
    settings.VT_API_KEY = "test_key"
    return VirusTotalProvider()

@pytest.mark.asyncio
async def test_missing_api_key():
    settings.VT_API_KEY = ""
    provider = VirusTotalProvider()
    result = await provider.analyze_url("http://example.com")
    assert not result.is_successful
    assert "Missing API Key" in result.error_message

@pytest.mark.asyncio
async def test_vt_disabled():
    settings.VT_ENABLED = False
    provider = VirusTotalProvider()
    result = await provider.analyze_url("http://example.com")
    assert not result.is_successful
    assert "Provider Disabled" in result.error_message

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_valid_response(mock_get, vt_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "attributes": {
                "last_analysis_stats": {"malicious": 5, "suspicious": 1}
            }
        }
    }
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = await vt_provider.analyze_url("http://malicious.com")
    
    assert result.is_successful
    assert len(result.indicators) == 2
    assert result.indicators[0]["severity"] == "critical"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_rate_limited(mock_get, vt_provider):
    # Setup mock to raise HTTPStatusError for 429
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    
    # We must patch asyncio.sleep to not actually sleep during the exponential backoff test
    with patch("asyncio.sleep", new_callable=AsyncMock):
        mock_get.side_effect = httpx.HTTPStatusError("Rate Limited", request=MagicMock(), response=mock_resp)
        result = await vt_provider.analyze_url("http://example.com")
        
        assert not result.is_successful
        assert "Rate Limited" in result.error_message

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_timeout_fallback(mock_get, vt_provider):
    with patch("asyncio.sleep", new_callable=AsyncMock):
        mock_get.side_effect = httpx.TimeoutException("Timeout")
        result = await vt_provider.analyze_url("http://example.com")
        
        assert not result.is_successful
        assert "Timeout" in result.error_message

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_404_not_found(mock_get, vt_provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.side_effect = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_resp)
    
    result = await vt_provider.analyze_url("http://newsite.com")
    assert result.is_successful
    assert len(result.indicators) == 0
