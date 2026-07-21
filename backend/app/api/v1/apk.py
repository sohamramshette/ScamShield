import os
import tempfile
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.database.session import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.apk_scan import APKScan
from app.services.apk_analyzer import analyze_apk
from app.services.threat_orchestrator import ThreatOrchestrator
from app.services.report_generator import generate_pdf_report
from fastapi.responses import FileResponse

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB

@router.post("/analyze")
async def analyze_apk_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".apk"):
        raise HTTPException(status_code=400, detail="Only APK files are supported.")
        
    # Read file content and check size limit
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB.")

    # Save to temp file
    fd, temp_path = tempfile.mkstemp(suffix=".apk")
    with os.fdopen(fd, 'wb') as f:
        f.write(content)

    threat_orchestrator = ThreatOrchestrator(db, []) # Simplified init

    try:
        # We run the analyzer
        scan = await analyze_apk(temp_path, current_user.id, db, threat_orchestrator)
        return {"id": scan.id, "status": "completed"}
    except Exception as e:
        logger.error(f"APK analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze APK")
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/{scan_id}")
def get_apk_scan(scan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = db.query(APKScan).options(
        joinedload(APKScan.permissions),
        joinedload(APKScan.components),
        joinedload(APKScan.certificates),
        joinedload(APKScan.iocs),
        joinedload(APKScan.libraries),
        joinedload(APKScan.yara_matches),
        joinedload(APKScan.mitre_tactics)
    ).filter(APKScan.id == scan_id, APKScan.user_id == current_user.id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return {
        "id": scan.id,
        "filename": scan.filename,
        "package_name": scan.package_name,
        "version": scan.version,
        "version_code": scan.version_code,
        "min_sdk": scan.min_sdk,
        "target_sdk": scan.target_sdk,
        "size_bytes": scan.size_bytes,
        "architecture": scan.architecture,
        "dex_count": scan.dex_count,
        "sha256": scan.sha256,
        "manifest_json": scan.manifest_json,
        "risk_score": scan.risk_score,
        "confidence": scan.confidence,
        "permission_risk": scan.permission_risk,
        "certificate_risk": scan.certificate_risk,
        "manifest_risk": scan.manifest_risk,
        "component_risk": scan.component_risk,
        "yara_risk": scan.yara_risk,
        "network_risk": scan.network_risk,
        "code_risk": scan.code_risk,
        "similarity_score": scan.similarity_score,
        "closest_sample_id": scan.closest_sample_id,
        "malware_family": scan.malware_family,
        "ai_family": scan.ai_family,
        "ai_summary": scan.ai_summary,
        "ai_behaviour": scan.ai_behaviour,
        "ai_impact": scan.ai_impact,
        "ai_actions": scan.ai_actions,
        "recommendations": scan.recommendations,
        "permissions": [{"permission": p.permission, "dangerous": p.dangerous, "severity": p.severity, "protection_level": p.protection_level} for p in scan.permissions],
        "components": [{"name": c.name, "type": c.component_type, "exported": c.exported} for c in scan.components],
        "certificates": [{"issuer": c.issuer, "subject": c.subject, "fingerprint": c.fingerprint, "algorithm": c.signature_algorithm, "trust_level": c.trust_level, "risk_level": c.risk_level, "self_signed": c.self_signed} for c in scan.certificates],
        "iocs": [{"type": i.ioc_type, "value": i.value, "severity": i.severity} for i in scan.iocs],
        "libraries": [{"name": l.name, "category": l.category, "risk": l.risk} for l in scan.libraries],
        "yara_matches": [{"rule": y.rule_name, "severity": y.severity, "description": y.description, "strings": y.strings_matched} for y in scan.yara_matches],
        "mitre_tactics": [{"tactic": m.tactic, "technique": m.technique, "severity": m.severity} for m in scan.mitre_tactics]
    }

@router.get("/{scan_id}/report")
def get_apk_report(scan_id: str, format: str = "pdf", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = db.query(APKScan).options(
        joinedload(APKScan.permissions),
        joinedload(APKScan.components),
        joinedload(APKScan.certificates),
        joinedload(APKScan.iocs),
        joinedload(APKScan.libraries),
        joinedload(APKScan.yara_matches),
        joinedload(APKScan.mitre_tactics)
    ).filter(APKScan.id == scan_id, APKScan.user_id == current_user.id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if format == "json":
        from fastapi.responses import JSONResponse
        # Return full scan dictionary for JSON dump
        data = {
            "id": scan.id, "package_name": scan.package_name, "risk_score": scan.risk_score,
            "ai_family": scan.ai_family, "ai_summary": scan.ai_summary, "ai_behaviour": scan.ai_behaviour,
            "yara_matches": [y.rule_name for y in scan.yara_matches]
        }
        return JSONResponse(content=data)
        
    if format == "csv":
        from fastapi.responses import PlainTextResponse
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Package", "Risk Score", "Family", "YARA Matches"])
        writer.writerow([scan.id, scan.package_name, scan.risk_score, scan.ai_family, len(scan.yara_matches)])
        return PlainTextResponse(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=apk_report_{scan_id}.csv"})
        
    pdf_path = generate_pdf_report(
        scan_id=scan.id,
        scan_type="APK Analysis",
        target=scan.package_name or scan.filename,
        risk_score=scan.risk_score,
        confidence=scan.confidence,
        explanation=scan.ai_summary or "No summary available",
        recommendations=scan.recommendations or "No recommendations available",
        threat_indicators=[{"indicator": i.value, "severity": i.severity} for i in scan.iocs]
    )
    return FileResponse(pdf_path, media_type='application/pdf', filename=f"apk_report_{scan_id}.pdf")
