import time
import asyncio
from sqlalchemy.orm import Session
from app.models.message_scan import MessageScan
from app.models.message_url import MessageURL
from app.models.message_phone import MessagePhone
from app.models.message_ioc import MessageIOC
from app.services.sms_parser import SMSParser, ParsedMessage
from app.services.ocr_service import ocr_service
from app.services.ai_service import generate_explanation
from app.services.threat_orchestrator import ThreatOrchestrator
from app.services.providers import ProviderRegistry

class MessageOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        providers = ProviderRegistry.get_enabled_providers()
        self.threat_orchestrator = ThreatOrchestrator(db, providers)
        
    async def process_message(self, user_id: int, platform: str, sender: str = None, receiver: str = None, text: str = None, image_bytes: bytes = None) -> int:
        start_time = time.time()
        
        # 1. OCR if image provided
        if image_bytes and not text:
            text = ocr_service.extract_text(image_bytes)
            
        if not text:
            raise ValueError("No text provided or extracted from image")
            
        # 2. Parsing
        parsed = SMSParser.parse(text)
        if sender:
            sender_parsed = SMSParser.parse(sender)
            parsed.phones.extend(sender_parsed.phones)
            parsed.emails.extend(sender_parsed.emails)
            if "@" in sender and sender not in parsed.emails:
                parsed.emails.append(sender)
            if any(c.isdigit() for c in sender) and sender not in parsed.phones:
                parsed.phones.append(sender)
        if receiver:
            receiver_parsed = SMSParser.parse(receiver)
            parsed.phones.extend(receiver_parsed.phones)
            parsed.emails.extend(receiver_parsed.emails)
        
        # 3. Create DB Record
        scan = MessageScan(
            user_id=user_id,
            platform=platform,
            sender=sender,
            receiver=receiver,
            language=parsed.language,
            message_text=parsed.normalized_text
        )
        self.db.add(scan)
        self.db.commit()
        
        # 4. IOC Extraction and Threat Intelligence
        url_tasks = []
        for url in parsed.urls[:5]:
            url_tasks.append(self._analyze_url(url, scan.id))
            
        await asyncio.gather(*url_tasks)
        
        for phone in parsed.phones[:5]:
            self._analyze_phone(phone, scan.id)
            
        # Add generic IOCs
        for email in parsed.emails: self._add_ioc(scan.id, "EMAIL", email)
        for wallet in parsed.wallets: self._add_ioc(scan.id, "WALLET", wallet)
        for upi in parsed.upis: self._add_ioc(scan.id, "UPI", upi)
        for ip in parsed.ips: self._add_ioc(scan.id, "IP", ip)
        for otp in parsed.otps: self._add_ioc(scan.id, "OTP", otp)
        for domain in parsed.domains: self._add_ioc(scan.id, "DOMAIN", domain)
        
        # 5. Social Engineering & AI (using Granite via AIService)
        prompt = f"Analyze this {platform} message for social engineering techniques (Urgency, Fear, Authority, Reward, Greed, Curiosity, Scarcity, Trust Exploitation). Determine the scam category (e.g., Bank Scam, OTP Scam, Courier Scam, Fake Job, Fake Support). Message content: '{parsed.normalized_text}'"
        
        # Pass real indicators from DB to AI instead of mock []
        # MessageIOC are added inside _add_ioc, let's fetch them now for the prompt.
        db_iocs = self.db.query(MessageIOC).filter(MessageIOC.scan_id == scan.id).all()
        real_indicators = [{"indicator": i.ioc_type, "severity": i.severity, "description": i.value} for i in db_iocs]
        
        explanation, recommendations = await generate_explanation(platform, prompt, 0, real_indicators)
        scan.ai_summary = explanation
        scan.recommendations = recommendations
        
        # Basic heuristic for scoring based on AI and parsed data
        scan.social_engineering_score = 75 if any(kw in explanation.lower() for kw in ['urgency', 'fear', 'scam', 'fraud']) else 20
        
        # Determine Scam Category heuristically for fast path
        lower_text = parsed.normalized_text.lower()
        if "otp" in lower_text or "code" in lower_text: scan.scam_type = "OTP Scam"
        elif "bank" in lower_text or "kyc" in lower_text: scan.scam_type = "Bank/KYC Scam"
        elif "delivery" in lower_text or "courier" in lower_text or "package" in lower_text: scan.scam_type = "Courier Scam"
        elif "job" in lower_text or "salary" in lower_text or "work from home" in lower_text: scan.scam_type = "Job Scam"
        elif "investment" in lower_text or "crypto" in lower_text or "yield" in lower_text: scan.scam_type = "Investment/Crypto Scam"
        elif "lottery" in lower_text or "prize" in lower_text or "won" in lower_text: scan.scam_type = "Lottery Scam"
        else: scan.scam_type = "Unknown"
        
        # 6. Confidence Breakdown & Final Risk
        scan.ocr_confidence = 90 if image_bytes else 100
        scan.threat_intel_confidence = 85
        scan.language_confidence = 95
        scan.reputation_confidence = 80
        scan.rule_engine_confidence = 90
        
        # Weighted average
        scan.confidence = int((scan.ocr_confidence + scan.threat_intel_confidence + scan.rule_engine_confidence) / 3)
        
        # Risk Score Calculation (0-100)
        base_risk = scan.social_engineering_score
        if parsed.urls: base_risk += 20
        if parsed.wallets: base_risk += 40
        if parsed.upis: base_risk += 30
        
        scan.risk_score = min(100, base_risk)
        scan.processing_time_ms = int((time.time() - start_time) * 1000)
        
        self.db.commit()
        return scan.id

    async def _analyze_url(self, url: str, scan_id: int):
        try:
            from app.services.risk_engine import evaluate_risk
            provider_results = await self.threat_orchestrator.analyze("url", url)
            risk_data = evaluate_risk(provider_results, [])
            
            m_url = MessageURL(
                scan_id=scan_id,
                url=url,
                provider_results=risk_data.get("providers", []),
                risk_score=risk_data.get("risk_score", 0)
            )
            self.db.add(m_url)
            
            # Auto-promote high risk to IOC
            if m_url.risk_score > 50:
                self._add_ioc(scan_id, "URL", url, "High", m_url.risk_score, risk_data)
        except Exception:
            self.db.add(MessageURL(scan_id=scan_id, url=url, risk_score=0))
            
    def _analyze_phone(self, phone: str, scan_id: int):
        # Offline phone heuristics
        reputation = "Unknown"
        scam_score = 0
        if phone.startswith("+234") or phone.startswith("+92"):
            reputation = "High Risk Country"
            scam_score = 80
            
        self.db.add(MessagePhone(
            scan_id=scan_id,
            number=phone,
            reputation=reputation,
            scam_score=scam_score
        ))
        
        if scam_score > 50:
            self._add_ioc(scan_id, "PHONE", phone, "High", scam_score)
            
    def _add_ioc(self, scan_id: int, ioc_type: str, value: str, severity: str = "Medium", confidence: int = 80, evidence: dict = None):
        self.db.add(MessageIOC(
            scan_id=scan_id,
            ioc_type=ioc_type,
            value=value,
            severity=severity,
            confidence=confidence,
            evidence=evidence
        ))
