from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.scan_repository import ScanRepository
from app.services.report_generator import generate_pdf_report

router = APIRouter()

@router.get("/", tags=["History"])
def get_history(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    repo = ScanRepository(db)
    return repo.get_all_scans_for_user(current_user.id)

@router.get("/report/{scan_id}", tags=["History"])
def download_report(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = ScanRepository(db)
    report = repo.get_scan_report(scan_id, current_user.id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    file_path = generate_pdf_report(
        scan_id=report.scan_id,
        scan_type=report.scan_type,
        target=report.target,
        risk_score=report.risk_score,
        confidence=report.confidence,
        explanation=report.explanation,
        recommendations=report.recommendations,
        threat_indicators=report.threat_indicators
    )
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Failed to generate report")
        
    return FileResponse(path=file_path, filename=f"ScamShield_Report_{scan_id}.pdf", media_type="application/pdf")
