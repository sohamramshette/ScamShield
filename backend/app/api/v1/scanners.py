from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.logging import log_scan_completed, log_scan_started
from app.database.session import get_db
from app.models.threat_indicator import ThreatIndicator
from app.models.user import User
from app.models.website_scan import WebsiteScan
from app.schemas.all_schemas import ScanRequest, WebsiteScanResponse
from app.services.ai_service import generate_explanation
from app.services.risk_engine import calculate_risk_score
from app.services.threat_intelligence import analyze_url

router = APIRouter()


@router.post("/website", response_model=WebsiteScanResponse, tags=["Website Scanner"])
async def scan_website(
    req: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Create pending scan
    new_scan = WebsiteScan(user_id=current_user.id, url=req.target, status="running")
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    log_scan_started(str(new_scan.id), "website")

    # Analyze Threat Intelligence
    indicators_data = await analyze_url(req.target)

    # Calculate Risk Score
    risk_score = calculate_risk_score(indicators_data)

    # Generate AI Explanation
    explanation, recommendation = await generate_explanation(
        scan_type="website",
        target=req.target,
        risk_score=risk_score,
        threat_indicators=indicators_data,
    )

    # Save Indicators
    for ind in indicators_data:
        db_ind = ThreatIndicator(
            scan_id=new_scan.id,
            scan_type="website",
            indicator=ind["indicator"],
            severity=ind["severity"],
        )
        db.add(db_ind)

    # Update Scan
    new_scan.status = "completed"
    new_scan.risk_score = risk_score
    new_scan.confidence = 90  # Mock confidence for MVP
    new_scan.ai_explanation = explanation
    new_scan.recommendations = recommendation

    db.commit()
    db.refresh(new_scan)

    log_scan_completed(str(new_scan.id), "website", risk_score)

    # Build Response
    indicators = (
        db.query(ThreatIndicator)
        .filter(
            ThreatIndicator.scan_id == new_scan.id,
            ThreatIndicator.scan_type == "website",
        )
        .all()
    )

    response = WebsiteScanResponse.model_validate(new_scan)
    response.threat_indicators = indicators

    return response


from app.models.qr_scan import QRScan
from app.schemas.all_schemas import QRScanResponse, UPIScanResponse

@router.post("/qr", response_model=QRScanResponse, tags=["QR Scanner"])
async def scan_qr(
    req: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_scan = QRScan(user_id=current_user.id, extracted_data=req.target, status="running")
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    log_scan_started(str(new_scan.id), "qr")
    indicators_data = await analyze_url(req.target)
    risk_score = calculate_risk_score(indicators_data)
    explanation, recommendation = await generate_explanation("qr", req.target, risk_score, indicators_data)

    for ind in indicators_data:
        db.add(ThreatIndicator(scan_id=new_scan.id, scan_type="qr", indicator=ind["indicator"], severity=ind["severity"]))

    new_scan.status = "completed"
    new_scan.risk_score = risk_score
    new_scan.confidence = 90
    new_scan.ai_explanation = explanation
    new_scan.recommendations = recommendation

    db.commit()
    db.refresh(new_scan)
    log_scan_completed(str(new_scan.id), "qr", risk_score)

    indicators = db.query(ThreatIndicator).filter(ThreatIndicator.scan_id == new_scan.id, ThreatIndicator.scan_type == "qr").all()
    response = QRScanResponse.model_validate(new_scan)
    response.threat_indicators = indicators
    return response

from app.services.threat_intelligence import analyze_url, analyze_upi_id

@router.post("/upi", response_model=UPIScanResponse, tags=["UPI Analyzer"])
async def scan_upi(
    req: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.upi_scan import UPIScan
    
    new_scan = UPIScan(user_id=current_user.id, upi_id=req.target, status="running")
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    log_scan_started(str(new_scan.id), "upi")
    indicators_data = analyze_upi_id(req.target)
    risk_score = calculate_risk_score(indicators_data)
    explanation, recommendation = await generate_explanation("upi", req.target, risk_score, indicators_data)
    
    for ind in indicators_data:
        db.add(ThreatIndicator(scan_id=new_scan.id, scan_type="upi", indicator=ind["indicator"], severity=ind["severity"]))

    new_scan.status = "completed"
    new_scan.risk_score = risk_score
    new_scan.confidence = 90
    new_scan.ai_explanation = explanation
    new_scan.recommendations = recommendation

    db.commit()
    db.refresh(new_scan)
    log_scan_completed(str(new_scan.id), "upi", risk_score)

    indicators = db.query(ThreatIndicator).filter(ThreatIndicator.scan_id == new_scan.id, ThreatIndicator.scan_type == "upi").all()
    
    # Map to expected response schema
    response = UPIScanResponse(
        id=str(new_scan.id),
        status=new_scan.status,
        upi_id=new_scan.upi_id,
        risk_score=new_scan.risk_score,
        confidence=new_scan.confidence,
        ai_explanation=new_scan.ai_explanation,
        recommendations=new_scan.recommendations,
        threat_indicators=[{"indicator": i.indicator, "severity": i.severity} for i in indicators],
        created_at=new_scan.created_at
    )
    return response
