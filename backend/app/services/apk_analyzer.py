import os
import logging
from sqlalchemy.orm import Session
from app.models.apk_scan import APKScan
from app.models.apk_permission import APKPermission
from app.models.apk_component import APKComponent
from app.models.apk_certificate import APKCertificate
from app.models.apk_ioc import APKIOC
from app.models.apk_library import APKLibrary
from app.models.apk_yara import APKYaraMatch
from app.models.apk_mitre import APKMitre
from app.services.apk_parser import APKParser
from app.services.threat_orchestrator import ThreatOrchestrator
from app.services.ai_service import generate_apk_investigation

logger = logging.getLogger(__name__)

async def analyze_apk(filepath: str, user_id: int, db: Session, threat_orchestrator: ThreatOrchestrator) -> APKScan:
    """
    Main orchestration function for APK analysis.
    """
    scan = APKScan(user_id=user_id, filename=os.path.basename(filepath))
    db.add(scan)
    db.flush() # Get scan.id

    try:
        # 1. Parse APK
        parser = APKParser(filepath)
        metadata = parser.get_metadata()
        
        scan.package_name = metadata.get("package_name")
        scan.version = metadata.get("version")
        scan.version_code = metadata.get("version_code")
        scan.min_sdk = metadata.get("min_sdk")
        scan.target_sdk = metadata.get("target_sdk")
        scan.compile_sdk = metadata.get("compile_sdk")
        scan.size_bytes = metadata.get("size_bytes")
        scan.architecture = metadata.get("architecture")
        scan.dex_count = metadata.get("dex_count")
        scan.sha256 = parser.get_hash()
        scan.manifest_json = metadata.get("manifest_json")

        # 2. Store Permissions
        permissions = parser.get_permissions()
        perm_risk_score = 0
        for perm in permissions:
            db.add(APKPermission(
                scan_id=scan.id,
                permission=perm["permission"],
                protection_level=perm["protection_level"],
                dangerous=perm["dangerous"],
                justification=perm["justification"],
                severity=perm["severity"]
            ))
            if perm["dangerous"]:
                perm_risk_score += 10 if perm["severity"] == "Critical" else 5

        # 3. Store Components
        components = parser.get_components()
        comp_risk_score = 0
        for comp in components:
            db.add(APKComponent(
                scan_id=scan.id,
                component_type=comp["component_type"],
                name=comp["name"][:250],
                exported=comp["exported"],
                enabled=comp["enabled"],
                permission=comp["permission"]
            ))
            if comp["exported"] and comp["component_type"] in ["Service", "Receiver"]:
                comp_risk_score += 5

        # 4. Store Certificates
        certs = parser.get_certificates()
        cert_risk_score = 0
        for cert in certs:
            db.add(APKCertificate(
                scan_id=scan.id,
                issuer=cert["issuer"][:250] if cert["issuer"] else None,
                subject=cert["subject"][:250] if cert["subject"] else None,
                fingerprint=cert["fingerprint"][:250] if cert["fingerprint"] else None,
                signature_algorithm=cert["signature_algorithm"],
                expired=cert["expired"],
                self_signed=cert["self_signed"],
                trust_level=cert.get("trust_level", "Unknown"),
                risk_level=cert.get("risk_level", "Unknown")
            ))
            if cert["self_signed"] or cert.get("trust_level") == "Untrusted":
                cert_risk_score += 25

        # 5. Libraries
        libs = parser.get_libraries()
        for lib in libs:
            db.add(APKLibrary(
                scan_id=scan.id,
                name=lib["name"],
                category=lib["category"],
                description=lib["description"],
                risk=lib["risk"]
            ))

        # 6. Extract IOCs
        raw_iocs = parser.extract_iocs()
        network_risk_score = min(50, len(raw_iocs) * 2)

        # 7. YARA Engine
        yara_results = parser.get_yara_matches()
        yara_risk_score = 0
        for result in yara_results:
            db.add(APKYaraMatch(
                scan_id=scan.id,
                rule_name=result["rule_name"],
                severity=result["severity"],
                description=result["description"],
                strings_matched=result["strings_matched"],
                offset=result["offset"],
                rule_source=result["rule_source"]
            ))
            yara_risk_score += 40 if result["severity"] == "High" else 15
            
        for ioc in raw_iocs:
            db.add(APKIOC(
                scan_id=scan.id,
                ioc_type=ioc["ioc_type"],
                value=ioc["value"][:250],
                severity=ioc["severity"]
            ))

        # 8. MITRE (Mock mapping for now based on components/perms)
        if perm_risk_score > 0:
            db.add(APKMitre(
                scan_id=scan.id,
                tactic="Collection",
                technique="T1114 - Email Collection",
                description="App requests sensitive data permissions.",
                severity="Medium"
            ))

        # 9. Threat Intelligence via Orchestrator
        from app.services.evidence_engine import EvidenceEngine
        from app.services.risk_engine import evaluate_risk
        import asyncio

        # Scan top 3 URLs to avoid long wait
        url_iocs = [ioc for ioc in raw_iocs if ioc["ioc_type"] == "URL"][:3]
        provider_tasks = []
        for ioc in url_iocs:
            provider_tasks.append(threat_orchestrator.analyze("url", ioc["value"]))
        
        url_results = await asyncio.gather(*provider_tasks, return_exceptions=True)
        all_provider_results = []
        for res in url_results:
            if isinstance(res, list):
                all_provider_results.extend(res)
                
        # Create offline indicators from static analysis
        offline_inds = []
        if perm_risk_score > 0: offline_inds.append({"severity": "high" if perm_risk_score > 20 else "medium", "description": "Dangerous permissions"})
        if cert_risk_score > 0: offline_inds.append({"severity": "high", "description": "Untrusted/Self-signed certificate"})
        if yara_results: offline_inds.append({"severity": "critical", "description": f"YARA match: {yara_results[0]['rule_name']}"})
        
        # Risk Evaluation
        risk_data = evaluate_risk(all_provider_results, offline_inds)
        
        scan.permission_risk = min(100, perm_risk_score)
        scan.certificate_risk = min(100, cert_risk_score)
        scan.manifest_risk = 0
        scan.component_risk = min(100, comp_risk_score)
        scan.yara_risk = min(100, yara_risk_score)
        
        # Network risk comes from the risk engine now
        scan.network_risk = min(100, risk_data["risk_score"])
        scan.code_risk = 0
        
        # Final combined score
        base_risk = (
            scan.permission_risk * 0.15 +
            scan.certificate_risk * 0.10 +
            scan.component_risk * 0.15 +
            scan.yara_risk * 0.40 +
            scan.network_risk * 0.20
        )
            
        scan.risk_score = min(100, int(base_risk))
        scan.confidence = risk_data["confidence"] if risk_data["confidence"] > 0 else 70

        # Similarity Engine
        previous = db.query(APKScan).filter(APKScan.package_name == scan.package_name, APKScan.id != scan.id).first()
        if previous:
            scan.similarity_score = 85
            scan.closest_sample_id = previous.id

        # 10. IBM Granite AI Investigation
        context = {
            "family": yara_results[0]["rule_name"] if yara_results else "Unknown",
            "yara": [r["rule_name"] for r in yara_results],
            "dangerous_perms": len([p for p in permissions if p["dangerous"]]),
            "iocs": len(raw_iocs)
        }
        
        investigation = await generate_apk_investigation(
            target=scan.package_name or "Unknown APK",
            risk_score=scan.risk_score,
            threat_indicators=context
        )
        
        scan.ai_family = investigation.get("family", "Unknown")
        scan.ai_summary = investigation.get("summary", "")
        scan.ai_behaviour = investigation.get("behaviour", "")
        scan.ai_impact = investigation.get("impact", "")
        scan.ai_actions = investigation.get("actions", "")
        
        scan.malware_family = scan.ai_family
        scan.recommendations = scan.ai_actions

        db.commit()
        return scan

    except Exception as e:
        db.rollback()
        logger.error(f"Error analyzing APK: {e}")
        raise e
