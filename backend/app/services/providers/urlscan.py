import asyncio
import httpx
from urllib.parse import urlparse
from app.services.providers.base import ThreatProvider, ProviderResult
from app.config.settings import settings
from app.core.logging import logger

class URLScanProvider(ThreatProvider):
    def __init__(self):
        self.api_key = settings.URLSCAN_API_KEY
        self.base_url = settings.URLSCAN_BASE_URL
        self.timeout = settings.URLSCAN_TIMEOUT_MS / 1000.0
        self.max_retries = settings.URLSCAN_MAX_RETRIES
        self.is_enabled = settings.URLSCAN_ENABLED and bool(self.api_key)

    def provider_name(self) -> str:
        return "urlscan"

    @property
    def trust_weight(self) -> float:
        return 0.85

    @property
    def cache_ttl_hours(self) -> int:
        return 12

    async def health_check(self) -> bool:
        if not self.is_enabled:
            return False
        return True

    def _create_client(self) -> httpx.AsyncClient:
        headers = {"API-Key": self.api_key}
        return httpx.AsyncClient(timeout=self.timeout, headers=headers)

    async def _execute_with_retries(self, client: httpx.AsyncClient, params: dict) -> httpx.Response:
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await client.get(self.base_url, params=params)
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
            results = raw_json.get("results", [])
            for res in results:
                verdicts = res.get("verdicts", {})
                overall = verdicts.get("overall", {})
                
                if overall.get("malicious"):
                    indicators.append({
                        "indicator": "URLScan: Malicious Activity",
                        "severity": "critical",
                        "description": "URLScan community and automated analysis flagged this target as malicious.",
                        "evidence_category": "threat"
                    })
                    # Break after finding the first malicious verdict for this target to avoid spam
                    break
        except Exception as e:
            logger.error(f"[URLScan] Error parsing response: {e}")
            
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

        # URLScan searches by domain or exact URL. Domain is broader and better for historic intel.
        try:
            domain = urlparse(url).netloc
            if not domain:
                domain = url
        except Exception:
            domain = url
            
        params = {
            "q": f"domain:{domain}",
            "size": 1
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
        if not self.is_enabled:
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                status="API_KEY_MISSING",
                confidence=0,
                error_message="Missing API Key"
            )

        params = {
            "q": f"ip:{ip}",
            "size": 1
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
        except Exception as e:
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                status="ERROR",
                confidence=0,
                error_message=f"Connection Error: {str(e)}"
            )
