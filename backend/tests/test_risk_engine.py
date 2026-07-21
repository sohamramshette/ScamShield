from app.services.risk_engine import calculate_risk_and_confidence, get_risk_level
from app.schemas.all_schemas import ThreatIndicatorSchema

def test_calculate_risk_and_confidence_empty():
    risk, conf = calculate_risk_and_confidence([])
    assert risk == 0
    assert conf == 90

def test_calculate_risk_and_confidence_various():
    indicators = [
        ThreatIndicatorSchema(indicator="Test1", severity="critical", category="threat"),
        ThreatIndicatorSchema(indicator="Test2", severity="high", category="threat"),
    ]
    risk, conf = calculate_risk_and_confidence(indicators)
    assert risk > 0
    assert conf > 0

def test_calculate_risk_score_cap():
    indicators = [
        ThreatIndicatorSchema(indicator="Test1", severity="critical", category="threat"),
        ThreatIndicatorSchema(indicator="Test2", severity="critical", category="threat"),
        ThreatIndicatorSchema(indicator="Test3", severity="critical", category="threat"),
        ThreatIndicatorSchema(indicator="Test4", severity="critical", category="threat"),
    ]
    risk, conf = calculate_risk_and_confidence(indicators)
    assert risk == 100
    assert conf <= 100

def test_get_risk_level():
    assert get_risk_level(0) == "Safe"
    assert get_risk_level(30) == "Low Risk"
    assert get_risk_level(50) == "Medium Risk"
    assert get_risk_level(75) == "High Risk"
    assert get_risk_level(90) == "Critical"
