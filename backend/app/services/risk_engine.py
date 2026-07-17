from app.core.logging import logger


def calculate_risk_score(threat_indicators: list[dict]) -> int:
    """
    Calculates a risk score from 0 to 100 based on threat indicators.
    0-20: Safe
    21-40: Low Risk
    41-60: Medium Risk
    61-80: High Risk
    81-100: Critical
    """
    logger.info("Calculating risk score based on threat indicators")
    if not threat_indicators:
        return 0

    score = 0
    for indicator in threat_indicators:
        severity = indicator.get("severity", "low")
        if severity == "critical":
            score += 40
        elif severity == "high":
            score += 25
        elif severity == "medium":
            score += 15
        elif severity == "low":
            score += 5

    # Cap the score at 100
    final_score = min(score, 100)
    logger.info(f"Calculated risk score: {final_score}")
    return final_score


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
