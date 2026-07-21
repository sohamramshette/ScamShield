import yara
import logging

logger = logging.getLogger(__name__)

# Basic YARA rules for Android malware detection
# In a real enterprise system, these would be loaded from a database or external feed
YARA_RULES = """
rule Android_Banking_Trojan {
    meta:
        description = "Detects common Android Banking Trojans"
        author = "ScamShield AI"
        severity = "High"
        mitre_technique = "T1417"
    strings:
        $s1 = "accessibility service" ascii nocase
        $s2 = "BIND_ACCESSIBILITY_SERVICE" ascii nocase
        $s3 = "android.permission.RECEIVE_SMS" ascii nocase
        $s4 = "android.permission.SEND_SMS" ascii nocase
        $overlay = "SYSTEM_ALERT_WINDOW" ascii nocase
    condition:
        ($s1 or $s2) and ($s3 or $s4) and $overlay
}

rule Android_Spyware {
    meta:
        description = "Detects potential Android Spyware capabilities"
        author = "ScamShield AI"
        severity = "Medium"
        mitre_technique = "T1421"
    strings:
        $p1 = "android.permission.RECORD_AUDIO" ascii nocase
        $p2 = "android.permission.CAMERA" ascii nocase
        $p3 = "android.permission.ACCESS_FINE_LOCATION" ascii nocase
        $p4 = "android.permission.READ_CONTACTS" ascii nocase
        $c1 = "MediaRecorder" ascii nocase
    condition:
        3 of ($p*) and $c1
}

rule Android_Dropper {
    meta:
        description = "Detects capabilities often used by droppers"
        author = "ScamShield AI"
        severity = "High"
        mitre_technique = "T1456"
    strings:
        $p1 = "android.permission.REQUEST_INSTALL_PACKAGES" ascii nocase
        $p2 = "android.permission.QUERY_ALL_PACKAGES" ascii nocase
        $s1 = "DexClassLoader" ascii nocase
        $s2 = "installPackage" ascii nocase
    condition:
        ($p1 or $p2) and ($s1 or $s2)
}

rule Android_RAT {
    meta:
        description = "Detects Remote Access Trojan characteristics"
        author = "ScamShield AI"
        severity = "Critical"
        mitre_technique = "T1449"
    strings:
        $s1 = "exec" ascii nocase
        $s2 = "Runtime.getRuntime().exec" ascii nocase
        $s3 = "ProcessBuilder" ascii nocase
        $s4 = "android.intent.action.BOOT_COMPLETED" ascii nocase
        $s5 = "WAKE_LOCK" ascii nocase
    condition:
        ($s1 or $s2 or $s3) and $s4 and $s5
}
"""

class YaraEngine:
    def __init__(self):
        try:
            self.rules = yara.compile(source=YARA_RULES)
        except Exception as e:
            logger.error(f"Failed to compile YARA rules: {e}")
            self.rules = None

    def scan_file(self, filepath: str) -> list[dict]:
        """
        Scans a file against the loaded YARA rules.
        """
        if not self.rules:
            return []

        try:
            matches = self.rules.match(filepath)
            results = []
            for match in matches:
                results.append({
                    "rule": match.rule,
                    "description": match.meta.get("description", "Unknown YARA Rule"),
                    "severity": match.meta.get("severity", "Medium"),
                    "mitre_technique": match.meta.get("mitre_technique", "Unknown")
                })
            return results
        except Exception as e:
            logger.error(f"YARA scan failed for {filepath}: {e}")
            return []

    def scan_strings(self, strings: list[str]) -> list[dict]:
        """
        Scan a list of extracted strings.
        """
        if not self.rules:
            return []
            
        data = "\\n".join(strings).encode("utf-8", errors="ignore")
        try:
            matches = self.rules.match(data=data)
            results = []
            for match in matches:
                results.append({
                    "rule": match.rule,
                    "description": match.meta.get("description", "Unknown YARA Rule"),
                    "severity": match.meta.get("severity", "Medium"),
                    "mitre_technique": match.meta.get("mitre_technique", "Unknown")
                })
            return results
        except Exception as e:
            logger.error(f"YARA string scan failed: {e}")
            return []
