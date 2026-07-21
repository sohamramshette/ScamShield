from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.message_orchestrator import MessageOrchestrator
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import json

router = APIRouter()

class AnalyzeResponse(BaseModel):
    id: int
    status: str

@router.post("/analyze", response_model=AnalyzeResponse, tags=["Message Analyzer"])
async def analyze_message(
    file: Optional[UploadFile] = File(None),
    raw_content: Optional[str] = Form(None),
    platform: str = Form(..., description="SMS or WhatsApp"),
    sender: Optional[str] = Form(None),
    receiver: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file and not raw_content:
        raise HTTPException(status_code=400, detail="Must provide either an image file or raw content")
        
    image_bytes = None
    if file:
        image_bytes = await file.read()
        
    orchestrator = MessageOrchestrator(db)
    
    # Process synchronously to return ID and results fast (for demo purposes)
    try:
        scan_id = await orchestrator.process_message(
            user_id=current_user.id,
            platform=platform,
            sender=sender,
            receiver=receiver,
            text=raw_content,
            image_bytes=image_bytes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"id": scan_id, "status": "completed"}

@router.get("/{scan_id}", tags=["Message Analyzer"])
async def get_message_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.message_scan import MessageScan
    scan = db.query(MessageScan).filter(MessageScan.id == scan_id, MessageScan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return {
        "id": scan.id,
        "platform": scan.platform,
        "sender": scan.sender,
        "receiver": scan.receiver,
        "language": scan.language,
        "message_text": scan.message_text,
        "processing_time_ms": scan.processing_time_ms,
        "scam_type": scan.scam_type,
        "social_engineering_score": scan.social_engineering_score,
        "ocr_confidence": scan.ocr_confidence,
        "threat_intel_confidence": scan.threat_intel_confidence,
        "language_confidence": scan.language_confidence,
        "reputation_confidence": scan.reputation_confidence,
        "rule_engine_confidence": scan.rule_engine_confidence,
        "confidence": scan.confidence,
        "risk_score": scan.risk_score,
        "ai_summary": scan.ai_summary,
        "recommendations": scan.recommendations,
        "urls": [{"url": u.url, "risk_score": u.risk_score, "provider_results": u.provider_results} for u in scan.urls],
        "phones": [{"number": p.number, "reputation": p.reputation, "scam_score": p.scam_score} for p in scan.phones],
        "iocs": [{"type": i.ioc_type, "value": i.value, "severity": i.severity, "confidence": i.confidence} for i in scan.iocs]
    }

@router.get("/{scan_id}/report", tags=["Message Analyzer"])
async def get_message_report(
    scan_id: int,
    format: str = "pdf",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.message_scan import MessageScan
    from app.services.report_generator import generate_pdf_report
    scan = db.query(MessageScan).filter(MessageScan.id == scan_id, MessageScan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    data = {
        "id": scan.id,
        "type": scan.platform,
        "target": scan.sender or "Unknown",
        "risk_score": scan.risk_score or 0,
        "confidence": scan.confidence or 0,
        "findings": [i.value for i in scan.iocs],
        "created_at": scan.created_at.isoformat() if scan.created_at else None
    }
    
    if format.lower() == "pdf":
        file_path = generate_pdf_report(
            scan_id=scan.id,
            scan_type=scan.platform,
            target=scan.sender or "Unknown",
            risk_score=scan.risk_score or 0,
            confidence=scan.confidence or 0,
            explanation=scan.ai_summary or "No explanation generated.",
            recommendations=scan.recommendations or "No recommendations available.",
            threat_indicators=[{"indicator": i.value, "severity": i.severity} for i in scan.iocs]
        )
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=message_report_{scan_id}.pdf"})
    else:
        return data
