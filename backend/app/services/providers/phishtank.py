import asyncio
import httpx
from app.services.providers.base import ThreatProvider, ProviderResult
from app.config.settings import settings
from app.core.logging import logger

class PhishTankProvider(ThreatProvider):
    def __init__(self):
        self.api_url = settings.PHISHTANK_API
        self.timeout = settings.PHISHTANK_TIMEOUT_MS / 1000.0
        self.max_retries = settings.PHISHTANK_MAX_RETRIES
        self.is_enabled = settings.PHISHTANK_ENABLED

    def provider_name(self) -> str:
        return "phishtank"

    @property
    def trust_weight(self) -> float:
        return 0.80

    @property
    def cache_ttl_hours(self) -> int:
        return 24

    async def health_check(self) -> bool:
        return self.is_enabled

    def _create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self.timeout)

    async def _execute_with_retries(self, client: httpx.AsyncClient, params: dict) -> httpx.Response:
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await client.post(self.api_url, data=params)
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
            results = raw_json.get("results", {})
            if results.get("in_database") and results.get("valid"):
                indicators.append({
                    "indicator": "PhishTank: Verified Phishing",
                    "severity": "critical",
                    "description": "This URL has been actively verified as a phishing site by PhishTank.",
                    "evidence_category": "threat"
                })
        except Exception as e:
            logger.error(f"[PhishTank] Error parsing response: {e}")
            
        return indicators

    async def analyze_url(self, url: str) -> ProviderResult:
        if not self.is_enabled:
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                status="API_KEY_MISSING",
                confidence=0,
                error_message="Provider Disabled"
            )

        params = {
            "url": url,
            "format": "json"
        }

        try:
            async with self._create_client() as client:
                response = await self._execute_with_retries(client, params)
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
        # IPs can be checked just like URLs in PhishTank
        return await self.analyze_url(f"http://{ip}")
