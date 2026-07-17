import pytest

from app.services.threat_intelligence import analyze_url


@pytest.mark.asyncio
async def test_analyze_safe_url():
    url = "https://www.google.com"
    indicators = await analyze_url(url)
    assert len(indicators) == 0


@pytest.mark.asyncio
async def test_analyze_http_url():
    url = "http://www.google.com"
    indicators = await analyze_url(url)
    assert len(indicators) == 1
    assert indicators[0]["indicator"] == "No SSL/TLS (HTTP)"
    assert indicators[0]["severity"] == "medium"


@pytest.mark.asyncio
async def test_analyze_scam_url():
    url = "https://scam-site.com"
    indicators = await analyze_url(url)
    assert len(indicators) == 2
    assert any(i["severity"] == "high" for i in indicators)
    assert any(i["severity"] == "critical" for i in indicators)


@pytest.mark.asyncio
async def test_analyze_typosquatting_url():
    url = "https://secure-login-update.com"
    indicators = await analyze_url(url)
    assert len(indicators) == 1
    assert indicators[0]["severity"] == "high"
