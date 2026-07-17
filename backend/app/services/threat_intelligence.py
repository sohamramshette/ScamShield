import asyncio

from app.core.logging import log_threat_api_called, logger


async def mock_check_virustotal(url: str):
    log_threat_api_called("VirusTotal", url)
    await asyncio.sleep(0.5)
    if "scam" in url or "phish" in url:
        return {
            "indicator": "Found in VirusTotal malicious database",
            "severity": "high",
        }
    return None


async def mock_check_google_safe_browsing(url: str):
    log_threat_api_called("Google Safe Browsing", url)
    await asyncio.sleep(0.3)
    if "scam" in url:
        return {"indicator": "Flagged by Google Safe Browsing", "severity": "critical"}
    return None


async def analyze_url(url: str) -> list[dict]:
    """
    Aggregates threat intelligence from multiple sources.
    Returns a list of threat indicators.
    """
    logger.info(f"Starting Threat Intelligence analysis for URL: {url}")
    indicators = []

    # In a real scenario, these would be concurrent HTTP calls
    vt_result = await mock_check_virustotal(url)
    if vt_result:
        indicators.append(vt_result)

    gsb_result = await mock_check_google_safe_browsing(url)
    if gsb_result:
        indicators.append(gsb_result)

    if url.startswith("http://"):
        indicators.append({"indicator": "No SSL/TLS (HTTP)", "severity": "medium"})

    if "secure-login" in url and "paypal" not in url:
        indicators.append(
            {"indicator": "Typosquatting/Suspicious Keywords", "severity": "high"}
        )

    return indicators
