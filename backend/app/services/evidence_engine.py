from typing import List
from app.services.providers.base import ProviderResult
from app.schemas.all_schemas import ThreatIndicatorSchema

class EvidenceEngine:
    @staticmethod
    def process_evidence(results: List[ProviderResult]) -> List[ThreatIndicatorSchema]:
        """
        Normalizes ProviderResults, merges evidence, removes duplicates,
        and translates into universal ThreatIndicators.
        """
        merged_categories = {}
        
        for res in results:
            if not res.is_successful:
                continue
                
            for ind in res.indicators:
                raw_indicator = ind.get("indicator", "")
                severity = ind.get("severity", "low")
                description = ind.get("description", "")
                ev_category = ind.get("evidence_category", "threat")
                
                # If it's a specific infrastructure/trust finding, keep its unique key
                if ev_category in ["infrastructure", "reconnaissance", "trust"]:
                    category_key = raw_indicator # E.g., "Expired Certificate"
                else:
                    # Normalize threat keys
                    lower_ind = raw_indicator.lower()
                    category_key = "suspicious"
                    if "malware" in lower_ind or "malicious" in lower_ind:
                        category_key = "malware"
                    elif "phishing" in lower_ind or "social engineering" in lower_ind.replace("_", " "):
                        category_key = "phishing"
                    elif "spam" in lower_ind:
                        category_key = "spam"
                    
                if category_key not in merged_categories:
                    merged_categories[category_key] = {
                        "severity": severity,
                        "providers": [res.provider_name],
                        "descriptions": [description] if description else [],
                        "confidence_weight": res.trust_weight,
                        "evidence_category": ev_category
                    }
                else:
                    # Provider agreement
                    if res.provider_name not in merged_categories[category_key]["providers"]:
                        merged_categories[category_key]["providers"].append(res.provider_name)
                        merged_categories[category_key]["confidence_weight"] += res.trust_weight
                    
                    if description and description not in merged_categories[category_key]["descriptions"]:
                        merged_categories[category_key]["descriptions"].append(description)
                        
                    # Upgrade severity if necessary
                    current_sev = merged_categories[category_key]["severity"]
                    sev_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
                    if sev_rank.get(severity, 1) > sev_rank.get(current_sev, 1):
                        merged_categories[category_key]["severity"] = severity

        final_indicators = []
        for key, data in merged_categories.items():
            providers_str = ", ".join(data["providers"])
            
            if data["evidence_category"] == "threat":
                indicator_title = f"{key.title()} Activity Detected ({providers_str})"
            else:
                indicator_title = f"{key} ({providers_str})"
                
            desc = " | ".join(data["descriptions"]) if data["descriptions"] else f"Flagged by {providers_str}"
            
            final_indicators.append(ThreatIndicatorSchema(
                indicator=indicator_title,
                severity=data["severity"],
                description=desc,
                evidence_category=data["evidence_category"]
            ))
            
        return final_indicators
