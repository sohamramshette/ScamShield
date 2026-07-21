import asyncio
import whois
from datetime import datetime, timezone
from urllib.parse import urlparse
from app.services.providers.base import ThreatProvider, ProviderResult
from app.config.settings import settings
from app.core.logging import logger

class WHOISProvider(ThreatProvider):
    def __init__(self):
        self.timeout = settings.WHOIS_TIMEOUT_MS / 1000.0
        self.max_retries = settings.WHOIS_MAX_RETRIES
        self.is_enabled = settings.WHOIS_ENABLED

    def provider_name(self) -> str:
        return "whois"

    @property
    def trust_weight(self) -> float:
        return 0.30

    async def health_check(self) -> bool:
        return self.is_enabled

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc if parsed.netloc else parsed.path
            domain = domain.split(":")[0]  # Remove port if present
            # Very basic domain extraction, typically you'd use tldextract
            parts = domain.split(".")
            if len(parts) > 2:
                domain = ".".join(parts[-2:])
            return domain
        except Exception:
            return url

    def _perform_whois(self, domain: str) -> dict:
        try:
            w = whois.whois(domain)
            return dict(w)
        except Exception as e:
            raise Exception(f"WHOIS lookup failed: {str(e)}")

    def _normalize_response(self, raw_json: dict) -> list[dict]:
        indicators = []
        try:
            creation_date = raw_json.get("creation_date")
            expiration_date = raw_json.get("expiration_date")
            
            # WHOIS library sometimes returns a list of dates
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
                
            if creation_date and isinstance(creation_date, datetime):
                # Ensure timezone aware for subtraction
                now = datetime.now(timezone.utc)
                creation_utc = creation_date.astimezone(timezone.utc) if creation_date.tzinfo else creation_date.replace(tzinfo=timezone.utc)
                age_days = (now - creation_utc).days
                
                if age_days < 30:
                    indicators.append({
                        "indicator": "Very New Domain",
                        "severity": "high",
                        "description": f"Domain was registered only {age_days} days ago. Attackers frequently use new domains.",
                        "evidence_category": "infrastructure"
                    })
                elif age_days > 1000:
                    indicators.append({
                        "indicator": "Long Established Domain",
                        "severity": "low",
                        "description": f"Domain is {age_days} days old. This generally indicates legitimate long-term infrastructure.",
                        "evidence_category": "trust"
                    })
                    
            if expiration_date and isinstance(expiration_date, datetime):
                now = datetime.now(timezone.utc)
                expiration_utc = expiration_date.astimezone(timezone.utc) if expiration_date.tzinfo else expiration_date.replace(tzinfo=timezone.utc)
                days_to_expire = (expiration_utc - now).days
                
                if 0 <= days_to_expire < 30:
                    indicators.append({
                        "indicator": "Domain Expires Soon",
                        "severity": "medium",
                        "description": f"Domain expires in {days_to_expire} days. This may indicate a throwaway domain or poor maintenance.",
                        "evidence_category": "infrastructure"
                    })

        except Exception as e:
            logger.error(f"[WHOIS] Error parsing response: {e}")
            
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

        domain = self._extract_domain(url)
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # Run the blocking whois call in a background thread with timeout
                raw_json = await asyncio.wait_for(
                    asyncio.to_thread(self._perform_whois, domain),
                    timeout=self.timeout
                )
                
                # Cleanup non-serializable objects from dict for JSON storage
                safe_json = {}
                for k, v in raw_json.items():
                    if isinstance(v, datetime):
                        safe_json[k] = v.isoformat()
                    elif isinstance(v, list) and all(isinstance(x, datetime) for x in v):
                        safe_json[k] = [x.isoformat() for x in v]
                    else:
                        safe_json[k] = str(v) if v is not None else None

                indicators = self._normalize_response(raw_json)
                
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
                if "No match for" in str(e) or "NOT FOUND" in str(e):
                    # Not found is a valid response, just no indicators
                    return ProviderResult(
                        provider_name=self.provider_name(),
                        trust_weight=self.trust_weight,
                        is_successful=True,
                        indicators=[],
                        raw_payload={"error": "Domain not found"}
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
        # IP WHOIS is technically different, but we'll try the same library for now
        return await self.analyze_url(ip)
