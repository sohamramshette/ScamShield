import math
import re
from urllib.parse import urlparse
from app.services.providers.base import ThreatProvider, ProviderResult
from app.core.logging import logger

SUSPICIOUS_KEYWORDS = ["login", "secure", "verify", "update", "banking", "account", "payment", "auth", "signin", "wallet"]
HIGH_RISK_TLDS = [".xyz", ".top", ".info", ".click", ".live", ".ru", ".cn", ".tk", ".ml", ".ga", ".cf", ".gq"]
LEGIT_DOMAINS = ["google.com", "paypal.com", "apple.com", "microsoft.com", "amazon.com", "github.com"]

def calculate_entropy(text: str) -> float:
    if not text:
        return 0
    entropy = 0
    for x in set(text):
        p_x = float(text.count(x)) / len(text)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    return entropy

class OfflineRuleEngineProvider(ThreatProvider):
    def provider_name(self) -> str:
        return "offline_rule_engine"

    @property
    def trust_weight(self) -> float:
        return 0.45

    async def health_check(self) -> bool:
        return True  # Offline engine is always healthy

    async def analyze_ip(self, ip: str) -> ProviderResult:
        # Re-use URL analysis for IP domains, as it flags IP Address Domains
        return await self.analyze_url(f"http://{ip}")

    async def analyze_url(self, url: str) -> ProviderResult:
        logger.info(f"Starting Offline Threat Analysis for URL: {url}")
        indicators = []
        
        try:
            if not url.startswith("http"):
                parsed_url = urlparse("http://" + url)
            else:
                parsed_url = urlparse(url)
                
            domain = parsed_url.netloc.lower()
            if ":" in domain:
                domain = domain.split(":")[0]
            
            path = parsed_url.path.lower()
            
            if url.startswith("http://"):
                indicators.append({"indicator": "Unencrypted Connection (HTTP)", "severity": "medium"})
                
            if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
                indicators.append({"indicator": "IP Address used as Domain", "severity": "critical"})
                
            if len(domain) > 30:
                indicators.append({"indicator": "Unusually long domain name", "severity": "medium"})
                
            subdomains = domain.split(".")
            if len(subdomains) > 4:
                indicators.append({"indicator": "Excessive subdomains", "severity": "high"})
                
            found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in domain or kw in path]
            if found_keywords:
                indicators.append({
                    "indicator": f"Suspicious keywords found: {', '.join(found_keywords)}", 
                    "severity": "high"
                })
                
            if any(domain.endswith(tld) for tld in HIGH_RISK_TLDS):
                indicators.append({"indicator": "High-risk Top Level Domain (TLD)", "severity": "high"})
                
            if domain.count("-") > 2:
                indicators.append({"indicator": "Excessive hyphens in domain", "severity": "medium"})
                
            if "xn--" in domain:
                indicators.append({"indicator": "Punycode domain (Potential Homograph Attack)", "severity": "critical"})
                
            for legit in LEGIT_DOMAINS:
                legit_name = legit.split(".")[0]
                if legit_name in domain and not domain.endswith(legit):
                    indicators.append({"indicator": f"Potential Typosquatting of {legit_name.capitalize()}", "severity": "critical"})
                    break
                    
            domain_entropy = calculate_entropy(domain)
            if domain_entropy > 4.0:
                indicators.append({"indicator": "High domain entropy (Random-looking characters)", "severity": "medium"})

            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=True,
                indicators=indicators
            )
        except Exception as e:
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                error_message=str(e)
            )

    async def analyze_upi_id(self, upi_id: str) -> ProviderResult:
        logger.info(f"Starting Offline Threat Analysis for UPI: {upi_id}")
        indicators = []
        
        try:
            if "@" not in upi_id:
                indicators.append({"indicator": "Invalid UPI Format: Missing '@'", "severity": "critical"})
                return ProviderResult(provider_name=self.provider_name(), trust_weight=self.trust_weight, is_successful=True, indicators=indicators)
                
            parts = upi_id.split("@")
            if len(parts) != 2:
                indicators.append({"indicator": "Invalid UPI Format: Multiple '@' symbols", "severity": "critical"})
                return ProviderResult(provider_name=self.provider_name(), trust_weight=self.trust_weight, is_successful=True, indicators=indicators)
                
            merchant, handle = parts
            
            if not merchant or not handle:
                indicators.append({"indicator": "Invalid UPI Format: Empty merchant or handle", "severity": "critical"})
                return ProviderResult(provider_name=self.provider_name(), trust_weight=self.trust_weight, is_successful=True, indicators=indicators)
                
            if not re.match(r"^[a-zA-Z0-9.\-_]+$", merchant):
                indicators.append({"indicator": "Invalid characters in merchant name", "severity": "high"})
                
            if not re.match(r"^[a-zA-Z]+$", handle):
                indicators.append({"indicator": "Invalid characters in bank handle", "severity": "high"})
                
            found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in merchant.lower()]
            if found_keywords:
                indicators.append({
                    "indicator": f"Suspicious keywords in merchant name: {', '.join(found_keywords)}", 
                    "severity": "high"
                })
                
            KNOWN_SCAM_HANDLES = ["paytmqr", "freecharge"]
            if handle.lower() in KNOWN_SCAM_HANDLES:
                indicators.append({"indicator": f"Handle '{handle}' frequently used in scams", "severity": "medium"})
                
            if len(merchant) > 40:
                indicators.append({"indicator": "Unusually long merchant name", "severity": "medium"})
                
            LEGIT_BUSINESSES = ["amazon", "flipkart", "google", "uber", "zomato", "swiggy", "netflix"]
            for legit in LEGIT_BUSINESSES:
                if legit in merchant.lower() and merchant.lower() != legit:
                    indicators.append({"indicator": f"Potential Typosquatting of {legit.capitalize()}", "severity": "critical"})
                    
            merch_entropy = calculate_entropy(merchant)
            if merch_entropy > 3.5:
                indicators.append({"indicator": "High merchant name entropy (Random-looking)", "severity": "medium"})
                
            if not indicators:
                indicators.append({"indicator": "Valid UPI Format", "severity": "low"})
                
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=True,
                indicators=indicators
            )
        except Exception as e:
            return ProviderResult(
                provider_name=self.provider_name(),
                trust_weight=self.trust_weight,
                is_successful=False,
                error_message=str(e)
            )
