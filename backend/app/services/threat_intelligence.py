import math
import re
from urllib.parse import urlparse

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

async def analyze_url(url: str) -> list[dict]:
    """
    Offline threat intelligence engine that calculates heuristics based on string analysis.
    """
    logger.info(f"Starting Offline Threat Analysis for URL: {url}")
    indicators = []
    
    # Pre-processing
    if not url.startswith("http"):
        # Assume http for parsing purposes if missing, but flag it later
        parsed_url = urlparse("http://" + url)
    else:
        parsed_url = urlparse(url)
        
    domain = parsed_url.netloc.lower()
    if ":" in domain:
        domain = domain.split(":")[0]
    
    path = parsed_url.path.lower()
    
    # 1. Scheme Check
    if url.startswith("http://"):
        indicators.append({"indicator": "Unencrypted Connection (HTTP)", "severity": "medium"})
        
    # 2. IP Address Domain
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
        indicators.append({"indicator": "IP Address used as Domain", "severity": "critical"})
        
    # 3. Domain Length
    if len(domain) > 30:
        indicators.append({"indicator": "Unusually long domain name", "severity": "medium"})
        
    # 4. Excessive Subdomains
    subdomains = domain.split(".")
    if len(subdomains) > 4:  # e.g., a.b.c.example.com
        indicators.append({"indicator": "Excessive subdomains", "severity": "high"})
        
    # 5. Suspicious Keywords
    found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in domain or kw in path]
    if found_keywords:
        indicators.append({
            "indicator": f"Suspicious keywords found: {', '.join(found_keywords)}", 
            "severity": "high"
        })
        
    # 6. High Risk TLDs
    if any(domain.endswith(tld) for tld in HIGH_RISK_TLDS):
        indicators.append({"indicator": "High-risk Top Level Domain (TLD)", "severity": "high"})
        
    # 7. Excessive Hyphens
    if domain.count("-") > 2:
        indicators.append({"indicator": "Excessive hyphens in domain", "severity": "medium"})
        
    # 8. Punycode
    if "xn--" in domain:
        indicators.append({"indicator": "Punycode domain (Potential Homograph Attack)", "severity": "critical"})
        
    # 9. Typosquatting Check (Basic)
    # Check if a legit domain name is hidden inside the string, but it's not the actual root domain
    # e.g. login-paypal.xyz -> root is xyz, paypal is just a substring
    for legit in LEGIT_DOMAINS:
        legit_name = legit.split(".")[0]
        if legit_name in domain and not domain.endswith(legit):
            indicators.append({"indicator": f"Potential Typosquatting of {legit_name.capitalize()}", "severity": "critical"})
            break
            
    # 10. URL Entropy
    domain_entropy = calculate_entropy(domain)
    if domain_entropy > 4.0: # Highly random string
        indicators.append({"indicator": "High domain entropy (Random-looking characters)", "severity": "medium"})

    return indicators

def analyze_upi_id(upi_id: str) -> list[dict]:
    """
    Validates and analyzes a UPI ID string.
    """
    logger.info(f"Starting Offline Threat Analysis for UPI: {upi_id}")
    indicators = []
    
    # Basic validation
    if "@" not in upi_id:
        indicators.append({"indicator": "Invalid UPI Format: Missing '@'", "severity": "critical"})
        return indicators
        
    parts = upi_id.split("@")
    if len(parts) != 2:
        indicators.append({"indicator": "Invalid UPI Format: Multiple '@' symbols", "severity": "critical"})
        return indicators
        
    merchant, handle = parts
    
    # 1. Validation
    if not merchant or not handle:
        indicators.append({"indicator": "Invalid UPI Format: Empty merchant or handle", "severity": "critical"})
        return indicators
        
    if not re.match(r"^[a-zA-Z0-9.\-_]+$", merchant):
        indicators.append({"indicator": "Invalid characters in merchant name", "severity": "high"})
        
    if not re.match(r"^[a-zA-Z]+$", handle):
        indicators.append({"indicator": "Invalid characters in bank handle", "severity": "high"})
        
    # 2. Suspicious Keywords
    found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in merchant.lower()]
    if found_keywords:
        indicators.append({
            "indicator": f"Suspicious keywords in merchant name: {', '.join(found_keywords)}", 
            "severity": "high"
        })
        
    # 3. Known Scam Handles (Simulated list)
    KNOWN_SCAM_HANDLES = ["paytmqr", "freecharge"]
    if handle.lower() in KNOWN_SCAM_HANDLES:
        indicators.append({"indicator": f"Handle '{handle}' frequently used in scams", "severity": "medium"})
        
    # 4. Length checks
    if len(merchant) > 40:
        indicators.append({"indicator": "Unusually long merchant name", "severity": "medium"})
        
    # 5. Typosquatting of legit businesses
    LEGIT_BUSINESSES = ["amazon", "flipkart", "google", "uber", "zomato", "swiggy", "netflix"]
    for legit in LEGIT_BUSINESSES:
        if legit in merchant.lower() and merchant.lower() != legit:
            indicators.append({"indicator": f"Potential Typosquatting of {legit.capitalize()}", "severity": "critical"})
            
    # 6. Random entropy
    merch_entropy = calculate_entropy(merchant)
    if merch_entropy > 3.5:
        indicators.append({"indicator": "High merchant name entropy (Random-looking)", "severity": "medium"})
        
    if not indicators:
        indicators.append({"indicator": "Valid UPI Format", "severity": "low"})
        
    return indicators
