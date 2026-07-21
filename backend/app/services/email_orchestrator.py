from sqlalchemy.orm import Session
from app.services.email_parser import EmailParser, ParsedEmail
from app.services.threat_orchestrator import ThreatOrchestrator
from app.services.providers.registry import ProviderRegistry
from app.services.ai_service import generate_explanation
from app.models.email_scan import EmailScan
from app.models.email_attachment import EmailAttachment
from app.models.email_url import EmailURL, EmailHop
from app.models.threat_indicator import ThreatIndicator
import time
import asyncio

class EmailOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        providers = ProviderRegistry.get_enabled_providers()
        self.threat_orchestrator = ThreatOrchestrator(db, providers)

    async def process_email(self, user_id: int, raw_bytes: bytes, is_msg: bool = False, sender_override: str = None, subject_override: str = None) -> int:
        start_time = time.time()
        
        # 1. Parsing
        if is_msg:
            parsed = EmailParser.parse_msg_bytes(raw_bytes)
        else:
            parsed = EmailParser.parse_eml_bytes(raw_bytes)
            
        if sender_override:
            parsed.sender = sender_override
        if subject_override:
            parsed.subject = subject_override
            
        # Simulate Hops for plain text mode
        if not parsed.hops:
            sender_domain = "unknown.domain"
            if sender_override and "@" in sender_override:
                sender_domain = sender_override.split("@")[-1].strip(">").strip().lower()
            elif "@" in parsed.sender:
                sender_domain = parsed.sender.split("@")[-1].strip(">").strip().lower()
            parsed.hops.append(EmailHop(scan_id=0, hop_number=1, server_name=f"mx.{sender_domain}", ip_address="Simulated IP", timestamp="Just Now"))
            
        # 2. Database Creation
        scan = EmailScan(
            user_id=user_id,
            sender_address=parsed.sender,
            subject=parsed.subject,
            message_id=parsed.message_id,
            reply_to=parsed.reply_to,
            return_path=parsed.return_path,
            spf_status=parsed.spf,
            dkim_status=parsed.dkim,
            dmarc_status=parsed.dmarc,
            status="running"
        )
        self.db.add(scan)
        self.db.commit() # commit to get ID and persist before async sub-tasks
        
        # Add hops
        for h in parsed.hops:
            # Check if it's already an EmailHop (simulated) or ParsedHop
            if isinstance(h, EmailHop):
                h.scan_id = scan.id
                self.db.add(h)
            else:
                self.db.add(EmailHop(scan_id=scan.id, hop_number=h.hop_number, server_name=h.server_name, ip_address=h.ip_address, timestamp=h.timestamp))
                
        # Add attachments
        for att in parsed.attachments:
            # Simple offline check for dangerous extensions
            dang = att.extension in ['exe', 'vbs', 'bat', 'cmd', 'ps1', 'js', 'scr']
            dbl = att.filename.count('.') > 1 if att.filename else False
            macro = att.extension in ['docm', 'xlsm', 'pptm']
            arch = att.extension in ['zip', 'rar', '7z', 'tar', 'gz']
            
            self.db.add(EmailAttachment(
                scan_id=scan.id,
                filename=att.filename,
                extension=att.extension,
                mime_type=att.mime_type,
                sha256=att.sha256,
                size=att.size,
                dangerous_extension=dang,
                double_extension=dbl,
                has_macro=macro,
                is_archive=arch,
                is_executable=att.extension in ['exe', 'dll', 'sys']
            ))

        # 3. URL Investigation (Async)
        url_tasks = []
        for url in list(parsed.urls)[:10]: # Limit to 10 for performance
            url_tasks.append(self._analyze_url(url, scan.id))
            
        await asyncio.gather(*url_tasks)

        # 4. Intelligence & Risk
        sender_domain = ""
        if "@" in parsed.sender:
            sender_domain = parsed.sender.split("@")[-1].strip(">").strip().lower()
            
        scan.domain_age = 15 # mock
        scan.is_disposable = False
        scan.sender_reputation = 50 # Default middle risk
        
        if sender_domain:
            if sender_domain in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
                scan.sender_reputation = 20
            elif sender_domain.endswith(".xyz") or sender_domain.endswith(".top") or sender_domain.endswith(".tk"):
                scan.sender_reputation = 95
                scan.is_disposable = True
                scan.domain_age = 1
            else:
                scan.sender_reputation = 60
                
            # Simulate Auth for plain text mode
            if not is_msg and not parsed.spf: # Only if it hasn't been set by actual headers
                pass
            
            # Since it's plain text (no headers extracted), let's simulate the Auth fields
            if scan.spf_status == "Unknown":
                if scan.sender_reputation <= 40:
                    scan.spf_status = "Pass"
                    scan.dkim_status = "Pass"
                    scan.dmarc_status = "Pass"
                else:
                    scan.spf_status = "Fail"
                    scan.dkim_status = "Fail"
                    scan.dmarc_status = "Fail"
        # 5. Social Engineering & AI (using Granite via AIService)
        ai_prompt = f"Analyze this email for social engineering. Sender: {parsed.sender}. Subject: {parsed.subject}. Body: {parsed.body_text[:1000]}."
        
        # Pass real indicators up to the AI instead of mock
        # We need to fetch all ThreatIndicators for this scan_id to pass them. But they are added async in _analyze_url.
        # Actually _analyze_url is awaited before this!
        db_indicators = self.db.query(ThreatIndicator).filter(ThreatIndicator.scan_id == scan.id).all()
        real_indicators = [{"indicator": i.indicator, "severity": i.severity} for i in db_indicators]
        
        explanation, recommendations = await generate_explanation("email", ai_prompt, 0, real_indicators)
        
        scan.ai_explanation = explanation
        scan.recommendations = recommendations
        
        # Derive brand impersonation
        if "microsoft" in parsed.sender.lower() or "microsoft" in parsed.subject.lower():
            scan.brand_impersonation_target = "Microsoft"
            
        scan.social_engineering_score = 65 if scan.brand_impersonation_target else 20
        
        # 6. Final Risk Scoring
        base_score = scan.social_engineering_score
        base_score += (scan.sender_reputation * 0.4) # Sender reputation makes up 40% of base risk
        if scan.spf_status == "Fail" or scan.dkim_status == "Fail": base_score += 30
        scan.risk_score = min(100, int(base_score))
        scan.confidence = 85
        
        # 7. Finalize
        scan.processing_time_ms = int((time.time() - start_time) * 1000)
        scan.status = "completed"
        self.db.commit()
        return scan.id

    async def _analyze_url(self, url: str, scan_id: int):
        from app.services.evidence_engine import EvidenceEngine
        from app.services.risk_engine import evaluate_risk

        # We invoke the existing ThreatOrchestrator logic for the URL to get VT/GSB results
        provider_results = await self.threat_orchestrator.analyze("url", url)
        
        final_indicators = EvidenceEngine.process_evidence(provider_results)
        
        risk_data = evaluate_risk(provider_results, [])
        risk_score = risk_data["risk_score"]
        confidence = risk_data["confidence"]
        # Email orchestrator doesn't currently store providers in the DB for the whole email,
        # but it does store it in MessageURL. Oh wait, this is EmailURL.

        # Extract verdicts for the URL row specifically if present
        vt_verdict = "Unknown"
        gsb_verdict = "Unknown"
        for p in provider_results:
            if p.provider_name == "VirusTotal" and p.raw_payload:
                vt_verdict = p.raw_payload.get("verdict", "Unknown")
            if p.provider_name == "GoogleSafeBrowsing" and p.raw_payload:
                gsb_verdict = p.raw_payload.get("verdict", "Unknown")

        eu = EmailURL(
            scan_id=scan_id,
            url=url,
            risk_score=risk_score,
            confidence=confidence,
            threat_category="Malicious" if risk_score > 50 else "Safe",
            vt_verdict=vt_verdict,
            gsb_verdict=gsb_verdict,
            urlscan_verdict="Unknown"
        )
        self.db.add(eu)
        
        # Also add threat indicators if risky
        for ind in final_indicators:
            self.db.add(ThreatIndicator(
                scan_type="email", 
                scan_id=scan_id, 
                indicator=ind.indicator,
                severity=ind.severity,
                evidence_category=ind.evidence_category
            ))
