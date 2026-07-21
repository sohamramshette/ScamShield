import pytest
import ssl
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from app.services.providers.ssl_inspector import SSLInspectorProvider
from app.config.settings import settings

@pytest.fixture
def ssl_provider():
    settings.SSL_ENABLED = True
    return SSLInspectorProvider()

@pytest.mark.asyncio
async def test_ssl_disabled():
    settings.SSL_ENABLED = False
    provider = SSLInspectorProvider()
    result = await provider.analyze_url("https://example.com")
    assert not result.is_successful
    assert "Disabled" in result.error_message

@pytest.mark.asyncio
async def test_ssl_http_target():
    settings.SSL_ENABLED = True
    provider = SSLInspectorProvider()
    result = await provider.analyze_url("http://example.com")
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "No SSL (HTTP)" in result.indicators[0]["indicator"]

@pytest.mark.asyncio
@patch("app.services.providers.ssl_inspector.socket.create_connection")
@patch("app.services.providers.ssl_inspector.ssl.create_default_context")
async def test_ssl_valid_cert(mock_ssl, mock_socket, ssl_provider):
    mock_context = MagicMock()
    mock_ssock = MagicMock()
    
    # Simulate valid dates
    future_date = (datetime.now(timezone.utc) + timedelta(days=365)).strftime('%b %d %H:%M:%S %Y GMT')
    past_date = (datetime.now(timezone.utc) - timedelta(days=10)).strftime('%b %d %H:%M:%S %Y GMT')
    
    mock_ssock.getpeercert.return_value = {
        "notBefore": past_date,
        "notAfter": future_date
    }
    
    # Setup context manager mocks
    mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock
    mock_ssl.return_value = mock_context
    
    result = await ssl_provider.analyze_url("https://example.com")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "Certificate Valid" in result.indicators[0]["indicator"]
    assert result.indicators[0]["evidence_category"] == "trust"

@pytest.mark.asyncio
@patch("app.services.providers.ssl_inspector.socket.create_connection")
@patch("app.services.providers.ssl_inspector.ssl.create_default_context")
async def test_ssl_expired_cert(mock_ssl, mock_socket, ssl_provider):
    mock_context = MagicMock()
    mock_ssock = MagicMock()
    
    # Simulate expired date
    past_date = (datetime.now(timezone.utc) - timedelta(days=10)).strftime('%b %d %H:%M:%S %Y GMT')
    way_past_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime('%b %d %H:%M:%S %Y GMT')
    
    mock_ssock.getpeercert.return_value = {
        "notBefore": way_past_date,
        "notAfter": past_date
    }
    
    mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock
    mock_ssl.return_value = mock_context
    
    result = await ssl_provider.analyze_url("https://example.com")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "Expired Certificate" in result.indicators[0]["indicator"]
    assert result.indicators[0]["severity"] == "critical"
    assert result.indicators[0]["evidence_category"] == "infrastructure"

@pytest.mark.asyncio
@patch("app.services.providers.ssl_inspector.socket.create_connection")
@patch("app.services.providers.ssl_inspector.ssl.create_default_context")
async def test_ssl_invalid_cert(mock_ssl, mock_socket, ssl_provider):
    mock_context = MagicMock()
    mock_ssock = MagicMock()
    
    # Simulate failure to get cert dictionary
    mock_ssock.getpeercert.side_effect = [b"binary_cert", Exception("Invalid cert")]
    
    mock_context.wrap_socket.return_value.__enter__.return_value = mock_ssock
    mock_ssl.return_value = mock_context
    
    result = await ssl_provider.analyze_url("https://example.com")
    
    assert result.is_successful
    assert len(result.indicators) == 1
    assert "Invalid or Missing" in result.indicators[0]["indicator"]
    assert result.indicators[0]["severity"] == "high"
