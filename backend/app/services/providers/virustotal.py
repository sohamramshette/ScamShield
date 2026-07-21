import asyncio
import base64
import httpx
from urllib.parse import urlparse
from app.services.providers.base import ThreatProvider, ProviderResult
from app.config.settings import settings
from app.core.logging import logger

class VirusTotalProvider(ThreatProvider):
    def __init__(self):
        self.api_key = settings.VT_API_KEY
        self.base_url = settings.VT_BASE_URL
        self.timeout = settings.VT_TIMEOUT_MS / 1000.0
        self.max_retries = settings.VT_MAX_RETRIES
        self.is_enabled = settings.VT_ENABLED and bool(self.api_key)

    def provider_name(self) -> str:
        return "virustotal"

    @property
    def trust_weight(self) -> float:
        return 1.00

    async def health_check(self) -> bool:
        if not self.is_enabled:
            return False
        # Lightweight ping could be added here
        return True
        
    def _create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers={"x-apikey": self.api_key, "accept": "application/json"},
            timeout=self.timeout
        )

    async def _execute_with_retries(self, client: httpx.AsyncClient, method: str, url: str) -> httpx.Response:
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                if method == "GET":
                    response = await client.get(url)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                # E.g. Rate limiting (429) or Server Error (5xx)
                if e.response.status_code == 429 or e.response.status_code >= 500:
                    last_exception = e
                    if attempt < self.max_retries:
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
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
            attributes = raw_json.get("data", {}).get("attributes", {})
            stats = attributes.get("last_analysis_stats", {})
            
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            
            if malicious > 0:
                indicators.append({
                    "indicator": "Malicious Activity Detected by VirusTotal",
                    "severity": "critical" if malicious >= 3 else "high",
                    "description": f"VirusTotal engines flagged this as malicious ({malicious} detections)."
                })
            
            if suspicious > 0:
                indicators.append({
                    "indicator": "Suspicious Activity Detected by VirusTotal",
                    "severity": "medium",
                    "description": f"VirusTotal engines flagged this as suspicious ({suspicious} detections)."
                })
                
            categories = attributes.get("categories", {})
            if categories:
                # E.g. phishing, malware
                cat_values = list(set(categories.values()))
                bad_cats = [c for c in cat_values if c in ["phishing", "malware", "spam"]]
                if bad_cats:
                    indicators.append({
                        "indicator": f"Categorized as: {', '.join(bad_cats)}",
                        "severity": "high"
                    })
        except Exception as e:
            logger.error(f"[VirusTotal] Error parsing response: {e}")
            
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

        # VT requires base64 url-safe string without padding
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        endpoint = f"{self.base_url}/urls/{url_id}"

        try:
            async with self._create_client() as client:
                response = await self._execute_with_retries(client, "GET", endpoint)
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
            # 404 means VT doesn't have it in the database. This is a successful empty response.
            if e.response.status_code == 404:
                return ProviderResult(
                    provider_name=self.provider_name(),
                    trust_weight=self.trust_weight,
                    is_successful=True,
                    indicators=[],
                    raw_payload={"error": "Not found in VT database"}
                )
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

        endpoint = f"{self.base_url}/ip_addresses/{ip}"

        try:
            async with self._create_client() as client:
                response = await self._execute_with_retries(client, "GET", endpoint)
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
            if e.response.status_code == 404:
                return ProviderResult(
                    provider_name=self.provider_name(),
                    trust_weight=self.trust_weight,
                    is_successful=True,
                    indicators=[],
                    raw_payload={"error": "Not found in VT database"}
                )
            error_msg = f"HTTP {e.response.status_code}"
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
