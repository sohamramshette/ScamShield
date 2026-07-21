from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.email_scan import EmailScan
from app.services.email_orchestrator import EmailOrchestrator
from pydantic import BaseModel
import asyncio
from typing import Optional

router = APIRouter()

class EmailRawRequest(BaseModel):
    raw_content: str

@router.post("/analyze", tags=["Email Analyzer"])
async def analyze_email(
    file: Optional[UploadFile] = File(None),
    raw_content: Optional[str] = Form(None),
    sender: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file and not raw_content:
        raise HTTPException(status_code=400, detail="Must provide either a file or raw content")
        
    raw_bytes = b""
    is_msg = False
    
    if file:
        raw_bytes = await file.read()
        if file.filename and file.filename.endswith(".msg"):
            is_msg = True
        if len(raw_bytes) > 25 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum 25MB allowed.")
    else:
        raw_bytes = raw_content.encode("utf-8")
        
    orchestrator = EmailOrchestrator(db)
    # Process synchronously for now to return ID immediately. For large loads, could be backgrounded.
    scan_id = await orchestrator.process_email(current_user.id, raw_bytes, is_msg, sender, subject)
    
    return {"id": scan_id, "status": "completed"}

@router.get("/{scan_id}", tags=["Email Analyzer"])
def get_email_scan(scan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = db.query(EmailScan).filter(EmailScan.id == scan_id, EmailScan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return {
        "id": scan.id,
        "subject": scan.subject,
        "sender_address": scan.sender_address,
        "reply_to": scan.reply_to,
        "return_path": scan.return_path,
        "status": scan.status,
        "processing_time_ms": scan.processing_time_ms,
        "spf_status": scan.spf_status,
        "dkim_status": scan.dkim_status,
        "dmarc_status": scan.dmarc_status,
        "sender_reputation": scan.sender_reputation,
        "domain_age": scan.domain_age,
        "is_disposable": scan.is_disposable,
        "brand_impersonation_target": scan.brand_impersonation_target,
        "social_engineering_score": scan.social_engineering_score,
        "risk_score": scan.risk_score,
        "confidence": scan.confidence,
        "ai_explanation": scan.ai_explanation,
        "recommendations": scan.recommendations,
        "created_at": scan.created_at,
        "attachments": [
            {
                "filename": a.filename, "extension": a.extension, "mime_type": a.mime_type, "sha256": a.sha256,
                "size": a.size, "dangerous_extension": a.dangerous_extension, "double_extension": a.double_extension,
                "has_macro": a.has_macro, "is_executable": a.is_executable
            } for a in scan.attachments
        ],
        "urls": [
            {
                "url": u.url, "risk_score": u.risk_score, "confidence": u.confidence, "threat_category": u.threat_category,
                "vt_verdict": u.vt_verdict, "gsb_verdict": u.gsb_verdict
            } for u in scan.urls
        ],
        "hops": [
            {
                "hop_number": h.hop_number, "server_name": h.server_name, "ip_address": h.ip_address, "timestamp": h.timestamp
            } for h in scan.hops
        ]
    }

from fastapi.responses import JSONResponse, FileResponse
import csv
import io
import os
from app.services.report_generator import generate_pdf_report

@router.get("/{scan_id}/export", tags=["Email Analyzer"])
def export_email_scan(scan_id: int, format: str = "json", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = get_email_scan(scan_id, db, current_user)
    
    if format == "json":
        return JSONResponse(content=data)
        
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Subject", "Sender", "Risk Score", "Confidence", "SPF", "DKIM", "DMARC"])
        writer.writerow([data["id"], data["subject"], data["sender_address"], data["risk_score"], data["confidence"], data["spf_status"], data["dkim_status"], data["dmarc_status"]])
        return JSONResponse(content={"csv": output.getvalue()}) # In a real app we'd return a streaming response
        
    elif format == "pdf":
        file_path = generate_pdf_report(
            scan_id=data["id"],
            scan_type="email",
            target=data["sender_address"],
            risk_score=data["risk_score"],
            confidence=data["confidence"],
            explanation=data["ai_explanation"],
            recommendations=data["recommendations"],
            threat_indicators=[] # can pull real indicators if needed
        )
        if os.path.exists(file_path):
            return FileResponse(path=file_path, filename=f"scamshield_email_{scan_id}.pdf", media_type='application/pdf')
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
        
    raise HTTPException(status_code=400, detail="Unsupported format")
