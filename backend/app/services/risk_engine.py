import yaml
import os
from app.core.logging import logger
from typing import List, Dict, Any, Tuple
from app.services.providers.base import ProviderResult

# Load weights from config
WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "provider_weights.yaml")
try:
    with open(WEIGHTS_FILE, "r") as f:
        PROVIDER_WEIGHTS = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Failed to load provider weights: {e}")
    PROVIDER_WEIGHTS = {
        "virustotal": 35,
        "google_safe_browsing": 30,
        "whois": 10,
        "ssl_inspector": 15,
        "urlscan": 10,
        "phishtank": 25,
        "abuseipdb": 20
    }

def evaluate_risk(provider_results: List[ProviderResult], offline_indicators: List[Dict]) -> Dict[str, Any]:
    """
    Calculates final risk score, confidence, analysis mode, and structured provider breakdown.
    """
    logger.info("Evaluating risk with real provider data")
    
    total_risk = 0
    structured_providers = []
    
    # Track overall confidence based on availability
    total_expected_providers = 7
    online_count = 0
    offline_count = 0
    
    for res in provider_results:
        # Determine contribution based on indicators
        contribution = 0
        result_text = "Clean"
        
        if res.status == "ONLINE" and res.is_successful:
            online_count += 1
            if res.indicators:
                # Basic mapping: if there are critical/high threat indicators, apply full weight
                # In a real engine this would be far more granular
                max_severity = "low"
                for ind in res.indicators:
                    sev = ind.get("severity", "low")
                    if sev == "critical": max_severity = "critical"
                    elif sev == "high" and max_severity != "critical": max_severity = "high"
                    elif sev == "medium" and max_severity not in ["critical", "high"]: max_severity = "medium"
                
                weight = PROVIDER_WEIGHTS.get(res.provider_name, 10)
                if max_severity == "critical": contribution = weight
                elif max_severity == "high": contribution = int(weight * 0.8)
                elif max_severity == "medium": contribution = int(weight * 0.5)
                elif max_severity == "low": contribution = int(weight * 0.2)
                
                # Trust indicators can lower risk
                has_trust = any(i.get("evidence_category") == "trust" for i in res.indicators)
                if has_trust:
                    contribution -= 5
                    
                result_text = res.indicators[0].get("description", "Threat detected")
            else:
                result_text = "No detections"
        elif res.status in ["TIMEOUT", "ERROR", "RATE_LIMITED", "API_KEY_MISSING", "OFFLINE"]:
            offline_count += 1
            result_text = res.error_message or "Unavailable"
            
        total_risk += max(0, contribution)
        
        structured_providers.append({
            "name": res.provider_name,
            "status": res.status,
            "result": result_text,
            "contribution": contribution,
            "confidence": res.confidence,
            "latency_ms": res.latency_ms
        })
        
    # Process offline rule engine indicators
    offline_contribution = 0
    if offline_indicators:
        for ind in offline_indicators:
            sev = ind.get("severity", "low")
            if sev == "critical": offline_contribution += 20
            elif sev == "high": offline_contribution += 15
            elif sev == "medium": offline_contribution += 10
            elif sev == "low": offline_contribution += 5
            
        total_risk += offline_contribution
        structured_providers.append({
            "name": "Offline Rule Engine",
            "status": "ONLINE",
            "result": f"{len(offline_indicators)} offline rules triggered",
            "contribution": offline_contribution,
            "confidence": 100,
            "latency_ms": 1
        })
        
    # Determine Analysis Mode and Final Confidence
    if online_count == 0 and not offline_indicators:
        analysis_mode = "UNKNOWN"
        final_confidence = 0
    elif online_count == 0 and offline_indicators:
        analysis_mode = "OFFLINE"
        final_confidence = 50
    elif online_count < 4:
        analysis_mode = "LIMITED"
        final_confidence = 60 + (online_count * 5)
    else:
        analysis_mode = "LIVE"
        final_confidence = min(99, 70 + (online_count * 5))
        
    final_risk = max(0, min(total_risk, 100))
    
    return {
        "risk_score": final_risk,
        "confidence": final_confidence,
        "analysis_mode": analysis_mode,
        "providers": structured_providers
    }

def get_risk_level(score: int) -> str:
    if score <= 20:
        return "Safe"
    elif score <= 40:
        return "Low Risk"
    elif score <= 60:
        return "Medium Risk"
    elif score <= 80:
        return "High Risk"
    else:
        return "Critical"
