import asyncio
import httpx
from urllib.parse import urlparse
import socket
from app.services.providers.base import ThreatProvider, ProviderResult
from app.config.settings import settings
from app.core.logging import logger

class AbuseIPDBProvider(ThreatProvider):
    def __init__(self):
        self.api_key = settings.ABUSEIPDB_API_KEY
        self.base_url = settings.ABUSEIPDB_BASE_URL
        self.timeout = settings.ABUSEIPDB_TIMEOUT_MS / 1000.0
        self.max_retries = settings.ABUSEIPDB_MAX_RETRIES
        self.is_enabled = settings.ABUSEIPDB_ENABLED and bool(self.api_key)

    def provider_name(self) -> str:
        return "abuseipdb"

    @property
    def trust_weight(self) -> float:
        return 0.90

    @property
    def cache_ttl_hours(self) -> int:
        return 12

    async def health_check(self) -> bool:
        if not self.is_enabled:
            return False
        return True

    def _create_client(self) -> httpx.AsyncClient:
        headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }
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
            data = raw_json.get("data", {})
            abuse_score = data.get("abuseConfidenceScore", 0)
            
            if abuse_score >= 80:
                indicators.append({
                    "indicator": "AbuseIPDB: High Abuse Score",
                    "severity": "critical",
                    "description": f"IP has an abuse confidence score of {abuse_score}%.",
                    "evidence_category": "threat"
                })
            elif abuse_score >= 40:
                indicators.append({
                    "indicator": "AbuseIPDB: Suspicious IP",
                    "severity": "medium",
                    "description": f"IP has an abuse confidence score of {abuse_score}%.",
                    "evidence_category": "reconnaissance"
                })
        except Exception as e:
            logger.error(f"[AbuseIPDB] Error parsing response: {e}")
            
        return indicators

    def _extract_ip(self, url: str) -> str:
        try:
            # Check if it's already an IP
            socket.inet_aton(url)
            return url
        except socket.error:
            pass
            
        try:
            domain = urlparse(url).netloc
            if not domain:
                domain = url
            domain = domain.split(":")[0] # strip port
            # Basic DNS resolution to get IP for abuseipdb
            ip = socket.gethostbyname(domain)
            return ip
        except Exception:
            return ""

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

        # Get IP asynchronously (socket is blocking, but we wrap the whole provider exec anyway?
        # Actually, gethostbyname is blocking. Let's do it in to_thread
        try:
            ip = await asyncio.wait_for(
                asyncio.to_thread(self._extract_ip, url), 
                timeout=self.timeout
            )
            if not ip:
                return ProviderResult(
                    provider_name=self.provider_name(),
                    trust_weight=self.trust_weight,
                    is_successful=True, # Successfully found nothing
                    indicators=[],
                    raw_payload={"error": "Could not resolve IP for domain"}
                )
        except Exception as e:
             return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=True,
                indicators=[],
                raw_payload={"error": f"DNS Resolution failed: {e}"}
            )

        params = {
            "ipAddress": ip,
            "maxAgeInDays": 90
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
        return await self.analyze_url(ip)
