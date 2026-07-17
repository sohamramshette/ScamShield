from app.services.risk_engine import calculate_risk_score, get_risk_level


def test_calculate_risk_score_empty():
    assert calculate_risk_score([]) == 0


def test_calculate_risk_score_various():
    indicators = [
        {"severity": "critical"},  # +40
        {"severity": "high"},  # +25
        {"severity": "medium"},  # +15
    ]
    assert calculate_risk_score(indicators) == 80


def test_calculate_risk_score_cap():
    indicators = [
        {"severity": "critical"},  # +40
        {"severity": "critical"},  # +40
        {"severity": "critical"},  # +40
    ]
    assert calculate_risk_score(indicators) == 100


def test_get_risk_level():
    assert get_risk_level(0) == "Safe"
    assert get_risk_level(30) == "Low Risk"
    assert get_risk_level(50) == "Medium Risk"
    assert get_risk_level(75) == "High Risk"
    assert get_risk_level(90) == "Critical"
