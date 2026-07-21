import asyncio
import httpx
from app.services.providers.base import ThreatProvider, ProviderResult
from app.config.settings import settings
from app.core.logging import logger

class GoogleSafeBrowsingProvider(ThreatProvider):
    def __init__(self):
        self.api_key = settings.GSB_API_KEY
        self.base_url = settings.GSB_BASE_URL
        self.timeout = settings.GSB_TIMEOUT_MS / 1000.0
        self.max_retries = settings.GSB_MAX_RETRIES
        self.is_enabled = settings.GSB_ENABLED and bool(self.api_key)

    def provider_name(self) -> str:
        return "google_safe_browsing"

    @property
    def trust_weight(self) -> float:
        return 1.00

    async def health_check(self) -> bool:
        if not self.is_enabled:
            return False
        return True

    def _create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.timeout
        )

    async def _execute_with_retries(self, client: httpx.AsyncClient, payload: dict) -> httpx.Response:
        last_exception = None
        params = {"key": self.api_key}
        for attempt in range(self.max_retries + 1):
            try:
                response = await client.post(self.base_url, params=params, json=payload)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 or e.response.status_code >= 500:
                    last_exception = e
                    if attempt < self.max_retries:
                        await asyncio.sleep(2 ** attempt)
                        continue
                raise e
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise e
        raise last_exception

    def _normalize_response(self, raw_json: dict) -> list[dict]:
        indicators = []
        try:
            matches = raw_json.get("matches", [])
            if not matches:
                return indicators
                
            for match in matches:
                threat_type = match.get("threatType", "UNKNOWN")
                platform_type = match.get("platformType", "ANY_PLATFORM")
                
                indicators.append({
                    "indicator": f"Google Safe Browsing: {threat_type.replace('_', ' ').title()}",
                    "severity": "critical",
                    "description": f"Flagged by Google Safe Browsing on {platform_type}."
                })
                
        except Exception as e:
            logger.error(f"[GSB] Error parsing response: {e}")
            
        return indicators

    async def analyze_url(self, url: str) -> ProviderResult:
        if not self.is_enabled:
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                status="API_KEY_MISSING",
                confidence=0,
                error_message="Missing API Key"
            )

        payload = {
            "client": {
                "clientId": "scamshield-ai",
                "clientVersion": "1.0.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": url}
                ]
            }
        }

        try:
            async with self._create_client() as client:
                response = await self._execute_with_retries(client, payload)
                raw_json = response.json()
                indicators = self._normalize_response(raw_json)
                
                return ProviderResult(
                    provider_name=self.provider_name(),
                    trust_weight=self.trust_weight,
                    is_successful=True,
                    indicators=indicators,
                    raw_payload=raw_json
                )
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}"
            status = "ERROR"
            if e.response.status_code == 429:
                error_msg = "Rate Limited"
                status = "RATE_LIMITED"
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                status=status,
                confidence=0,
                error_message=error_msg
            )
        except Exception as e:
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                status="ERROR",
                confidence=0,
                error_message=f"Connection Error: {str(e)}"
            )

    async def analyze_ip(self, ip: str) -> ProviderResult:
        # GSB uses the exact same threatEntries payload for IPs as URLs (it treats IPs as URLs)
        return await self.analyze_url(ip)
