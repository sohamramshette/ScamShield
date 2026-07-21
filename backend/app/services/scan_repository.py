from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.website_scan import WebsiteScan
from app.models.qr_scan import QRScan
from app.models.upi_scan import UPIScan
from app.models.threat_indicator import ThreatIndicator

from app.models.email_scan import EmailScan

class ScanReport(BaseModel):
    scan_id: str
    scan_type: str
    target: str
    risk_score: int
    confidence: int
    explanation: str
    recommendations: str
    threat_indicators: List[dict]

class ScanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_scan_report(self, scan_id: str, user_id: int) -> Optional[ScanReport]:
        # Since scan_id might be numeric but passed as string, we try all tables
        # Website Scan
        website = self.db.query(WebsiteScan).filter(WebsiteScan.id == int(scan_id), WebsiteScan.user_id == user_id).first() if str(scan_id).isdigit() else None
        if website:
            return self._build_report(website, str(website.id), "website", website.url)
            
        # QR Scan
        qr = self.db.query(QRScan).filter(QRScan.id == int(scan_id), QRScan.user_id == user_id).first() if str(scan_id).isdigit() else None
        if qr:
            return self._build_report(qr, str(qr.id), "qr", qr.extracted_data)
            
        # UPI Scan
        upi = self.db.query(UPIScan).filter(UPIScan.id == int(scan_id) if str(scan_id).isdigit() else UPIScan.id == scan_id, UPIScan.user_id == user_id).first()
        if upi:
            return self._build_report(upi, str(upi.id), "upi", upi.upi_id)
            
        # Email Scan
        email = self.db.query(EmailScan).filter(EmailScan.id == int(scan_id), EmailScan.user_id == user_id).first() if str(scan_id).isdigit() else None
        if email:
            return self._build_report(email, str(email.id), "email", email.subject or email.sender_address)
            
        # Message Scan
        from app.models.message_scan import MessageScan
        message = self.db.query(MessageScan).filter(MessageScan.id == int(scan_id), MessageScan.user_id == user_id).first() if str(scan_id).isdigit() else None
        if message:
            return self._build_report(message, str(message.id), "message", message.platform + " Message")
            
        return None

    def get_all_scans_for_user(self, user_id: int):
        from app.models.message_scan import MessageScan
        websites = self.db.query(WebsiteScan).filter(WebsiteScan.user_id == user_id).all()
        qrs = self.db.query(QRScan).filter(QRScan.user_id == user_id).all()
        upis = self.db.query(UPIScan).filter(UPIScan.user_id == user_id).all()
        emails = self.db.query(EmailScan).filter(EmailScan.user_id == user_id).all()
        messages = self.db.query(MessageScan).filter(MessageScan.user_id == user_id).all()
        
        # Combine and sort by created_at desc
        combined = []
        for w in websites:
            combined.append({"id": w.id, "type": "website", "target": w.url, "risk_score": w.risk_score, "created_at": w.created_at})
        for q in qrs:
            combined.append({"id": q.id, "type": "qr", "target": q.extracted_data, "risk_score": q.risk_score, "created_at": q.created_at})
        for u in upis:
            combined.append({"id": u.id, "type": "upi", "target": u.upi_id, "risk_score": u.risk_score, "created_at": u.created_at})
        for e in emails:
            combined.append({"id": e.id, "type": "email", "target": e.subject or e.sender_address, "risk_score": e.risk_score, "created_at": e.created_at})
        for m in messages:
            combined.append({"id": m.id, "type": "message", "target": m.platform + " Message", "risk_score": m.risk_score, "created_at": m.created_at})
            
        combined.sort(key=lambda x: x["created_at"], reverse=True)
        return combined

    def _build_report(self, db_obj, scan_id: str, scan_type: str, target: str) -> ScanReport:
        indicators = self.db.query(ThreatIndicator).filter(
            ThreatIndicator.scan_id == db_obj.id,
            ThreatIndicator.scan_type == scan_type
        ).all()
        
        return ScanReport(
            scan_id=scan_id,
            scan_type=scan_type,
            target=target,
            risk_score=db_obj.risk_score or 0,
            confidence=db_obj.confidence or 0,
            explanation=db_obj.ai_explanation or "No explanation available",
            recommendations=db_obj.recommendations or "No recommendations available",
            threat_indicators=[{"indicator": i.indicator, "severity": i.severity} for i in indicators]
        )
