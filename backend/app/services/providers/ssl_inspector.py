import asyncio
import ssl
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse
from app.services.providers.base import ThreatProvider, ProviderResult
from app.config.settings import settings
from app.core.logging import logger

class SSLInspectorProvider(ThreatProvider):
    def __init__(self):
        self.timeout = settings.SSL_TIMEOUT_MS / 1000.0
        self.max_retries = settings.SSL_MAX_RETRIES
        self.is_enabled = settings.SSL_ENABLED

    def provider_name(self) -> str:
        return "ssl_inspector"

    @property
    def trust_weight(self) -> float:
        return 0.25

    @property
    def cache_ttl_hours(self) -> int:
        return 6

    async def health_check(self) -> bool:
        return self.is_enabled

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc if parsed.netloc else parsed.path
            domain = domain.split(":")[0]
            return domain
        except Exception:
            return url

    def _perform_ssl_handshake(self, domain: str) -> dict:
        context = ssl.create_default_context()
        # We don't want it to fail connection entirely just because it's expired,
        # we want to fetch the cert and inspect it!
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((domain, 443), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert(binary_form=True)
                
                # To get dictionary form including dates
                context.verify_mode = ssl.CERT_REQUIRED
                try:
                    # Actually get the parsed dict for easy fields
                    cert_dict = ssock.getpeercert()
                    return cert_dict
                except Exception:
                    # If it fails verification (e.g. self-signed, expired), getpeercert() with CERT_REQUIRED
                    # might throw, or if we can't get it, we just return a partial flag.
                    return {"_error_verification": True}
                    
    def _normalize_response(self, raw_json: dict) -> list[dict]:
        indicators = []
        
        if raw_json.get("_error_verification") or not raw_json:
            indicators.append({
                "indicator": "SSL Certificate Invalid or Missing",
                "severity": "high",
                "description": "The SSL certificate could not be fully verified, is self-signed, or is missing entirely.",
                "evidence_category": "infrastructure"
            })
            return indicators
            
        try:
            not_after = raw_json.get("notAfter")
            not_before = raw_json.get("notBefore")
            
            if not_after:
                expire_date = ssl.cert_time_to_seconds(not_after)
                now = datetime.now(timezone.utc).timestamp()
                
                if expire_date < now:
                    indicators.append({
                        "indicator": "Expired Certificate",
                        "severity": "critical",
                        "description": "The SSL certificate has expired.",
                        "evidence_category": "infrastructure"
                    })
                elif (expire_date - now) < (30 * 86400):
                    indicators.append({
                        "indicator": "Certificate Expires Soon",
                        "severity": "low",
                        "description": f"The SSL certificate expires in less than 30 days.",
                        "evidence_category": "infrastructure"
                    })
                else:
                    indicators.append({
                        "indicator": "Certificate Valid",
                        "severity": "low",
                        "description": "The SSL certificate is active and valid for a reasonable timeframe.",
                        "evidence_category": "trust"
                    })
                    
        except Exception as e:
            logger.error(f"[SSL] Error parsing response: {e}")
            
        return indicators

    async def analyze_url(self, url: str) -> ProviderResult:
        if not self.is_enabled:
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                status="OFFLINE",
                confidence=0,
                error_message="Provider Disabled"
            )

        # Only run on https or pure domain
        if url.startswith("http://"):
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=True,
                indicators=[{
                    "indicator": "No SSL (HTTP)",
                    "severity": "high",
                    "description": "The target uses unencrypted HTTP.",
                    "evidence_category": "infrastructure"
                }],
                raw_payload={"error": "HTTP target"}
            )

        domain = self._extract_domain(url)
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                raw_json = await asyncio.wait_for(
                    asyncio.to_thread(self._perform_ssl_handshake, domain),
                    timeout=self.timeout
                )

                indicators = self._normalize_response(raw_json)
                
                # Make safe for DB
                safe_json = {k: str(v) for k, v in raw_json.items()}
                
                return ProviderResult(
                    provider_name=self.provider_name(),
                    trust_weight=self.trust_weight,
                    is_successful=True,
                    indicators=indicators,
                    raw_payload=safe_json
                )
                
            except asyncio.TimeoutError as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return ProviderResult(
                    provider_name=self.provider_name(),
                    trust_weight=self.trust_weight,
                    is_successful=False,
                    status="TIMEOUT",
                    confidence=0,
                    error_message="Timeout"
                )
            except Exception as e:
                last_exception = e
                if "getaddrinfo failed" in str(e) or "nodename nor servname" in str(e):
                    # DNS failure
                    return ProviderResult(
                        provider_name=self.provider_name(),
                        trust_weight=self.trust_weight,
                        is_successful=True,
                        indicators=[{
                            "indicator": "Domain Resolution Failed",
                            "severity": "critical",
                            "description": "The domain does not exist or has no DNS records.",
                            "evidence_category": "infrastructure"
                        }],
                        raw_payload={"error": "DNS Resolution Failed"}
                    )
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return ProviderResult(
                    provider_name=self.provider_name(),
                    trust_weight=self.trust_weight,
                    is_successful=False,
                    status="ERROR",
                    confidence=0,
                    error_message=str(e)
                )

        return ProviderResult(
            provider_name=self.provider_name(),
            trust_weight=self.trust_weight,
            is_successful=False,
            status="ERROR",
            confidence=0,
            error_message=str(last_exception)
        )

    async def analyze_ip(self, ip: str) -> ProviderResult:
        return await self.analyze_url(ip)
