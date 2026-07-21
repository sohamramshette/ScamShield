import logging
import hashlib
import re
import os
import json
from typing import Dict, Any, List
from collections import defaultdict

try:
    from androguard.core.apk import APK
    from androguard.core.dex import DEX
    import yara
    ANDROGUARD_AVAILABLE = True
except ImportError:
    ANDROGUARD_AVAILABLE = False

logger = logging.getLogger(__name__)

# Basic regex for extracting URLs and IPs
URL_REGEX = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

DANGEROUS_PERMISSIONS = {
    "android.permission.READ_SMS": "High",
    "android.permission.SEND_SMS": "High",
    "android.permission.RECEIVE_SMS": "High",
    "android.permission.READ_CONTACTS": "Medium",
    "android.permission.READ_CALL_LOG": "High",
    "android.permission.WRITE_SETTINGS": "Medium",
    "android.permission.REQUEST_INSTALL_PACKAGES": "Critical",
    "android.permission.SYSTEM_ALERT_WINDOW": "Critical",
    "android.permission.QUERY_ALL_PACKAGES": "High",
    "android.permission.RECORD_AUDIO": "Medium",
    "android.permission.CAMERA": "Medium",
    "android.permission.ACCESS_FINE_LOCATION": "Medium"
}

KNOWN_LIBRARIES = {
    "com/google/firebase": {"name": "Firebase", "category": "Analytics/Backend", "description": "Google Firebase SDK", "risk": "Low"},
    "retrofit2/": {"name": "Retrofit", "category": "Networking", "description": "Type-safe HTTP client", "risk": "Low"},
    "okhttp3/": {"name": "OkHttp", "category": "Networking", "description": "HTTP client", "risk": "Low"},
    "com/facebook/": {"name": "Facebook SDK", "category": "Social", "description": "Facebook integration", "risk": "Medium"},
    "com/google/android/gms": {"name": "Google Play Services", "category": "Platform", "description": "Google Services", "risk": "Low"},
    "com/google/android/gms/ads": {"name": "AdMob", "category": "Advertising", "description": "Google AdMob", "risk": "Medium"},
    "com/bumptech/glide": {"name": "Glide", "category": "Media", "description": "Image loading framework", "risk": "Low"},
    "com/scottyab/rootbeer": {"name": "RootBeer", "category": "Security", "description": "Root detection library", "risk": "Low"}
}

class APKParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.apk = None
        self.dex_files = []
        if ANDROGUARD_AVAILABLE:
            try:
                self.apk = APK(self.filepath)
                # Load dex files for library detection
                for dex_data in self.apk.get_all_dex():
                    self.dex_files.append(DEX(dex_data))
            except Exception as e:
                logger.error(f"Failed to parse APK with androguard: {e}")
        else:
            logger.error("Androguard is not installed.")

    def get_hash(self) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(self.filepath, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""

    def get_metadata(self) -> Dict[str, Any]:
        if not self.apk:
            return {}

        size_bytes = os.path.getsize(self.filepath) if os.path.exists(self.filepath) else 0

        # Try to parse XML to JSON
        manifest_json = "{}"
        try:
            # We'll just build a simple representation for now
            manifest_dict = {
                "package": self.apk.get_package(),
                "activities": self.apk.get_activities(),
                "services": self.apk.get_services(),
                "receivers": self.apk.get_receivers(),
                "providers": self.apk.get_providers(),
            }
            manifest_json = json.dumps(manifest_dict)
        except Exception:
            pass

        return {
            "package_name": self.apk.get_package(),
            "version": self.apk.get_androidversion_name(),
            "version_code": int(self.apk.get_androidversion_code() or 0),
            "min_sdk": int(self.apk.get_min_sdk_version() or 0),
            "target_sdk": int(self.apk.get_target_sdk_version() or 0),
            "compile_sdk": 0,
            "size_bytes": size_bytes,
            "architecture": "Mixed" if self.apk.get_libraries() else "Java/Kotlin Only",
            "dex_count": len(self.dex_files),
            "manifest_json": manifest_json
        }

    def get_permissions(self) -> List[Dict[str, Any]]:
        if not self.apk:
            return []

        permissions = []
        for perm in self.apk.get_permissions():
            is_dangerous = perm in DANGEROUS_PERMISSIONS
            severity = DANGEROUS_PERMISSIONS.get(perm, "Low")
            
            protection = "Normal"
            if is_dangerous:
                protection = "Dangerous"
            elif "signature" in perm.lower():
                protection = "Signature"

            permissions.append({
                "permission": perm,
                "dangerous": is_dangerous,
                "severity": severity,
                "justification": "Used for " + perm.split(".")[-1].replace("_", " ").lower() if is_dangerous else None,
                "protection_level": protection
            })
        return permissions

    def get_components(self) -> List[Dict[str, Any]]:
        if not self.apk:
            return []

        components = []
        for item in self.apk.get_activities():
            components.append({"component_type": "Activity", "name": item, "exported": "exported" in item.lower(), "enabled": True})
        for item in self.apk.get_services():
            components.append({"component_type": "Service", "name": item, "exported": "exported" in item.lower(), "enabled": True})
        for item in self.apk.get_receivers():
            components.append({"component_type": "Receiver", "name": item, "exported": "exported" in item.lower(), "enabled": True})
        for item in self.apk.get_providers():
            components.append({"component_type": "Provider", "name": item, "exported": "exported" in item.lower(), "enabled": True})

        return components

    def get_certificates(self) -> List[Dict[str, Any]]:
        if not self.apk:
            return []

        certs = []
        try:
            for cert in self.apk.get_certificates():
                issuer = repr(cert.issuer.human_friendly)
                subject = repr(cert.subject.human_friendly)
                self_signed = issuer == subject
                
                # Trust evaluation
                trust_level = "Trusted"
                risk_level = "Low"
                if self_signed:
                    trust_level = "Untrusted"
                    risk_level = "High"

                certs.append({
                    "issuer": issuer,
                    "subject": subject,
                    "fingerprint": cert.sha256_fingerprint.replace(" ", ""),
                    "signature_algorithm": cert.signature_algo,
                    "self_signed": self_signed,
                    "expired": False, # Simplified
                    "trust_level": trust_level,
                    "risk_level": risk_level
                })
        except Exception as e:
            logger.warning(f"Error extracting certificates: {e}")
            
        return certs

    def extract_iocs(self) -> List[Dict[str, Any]]:
        if not self.apk:
            return []

        iocs = []
        unique_urls = set()
        unique_ips = set()

        try:
            with open(self.filepath, "rb") as f:
                data = f.read()
                strings = re.findall(b'[ -~]{5,}', data)
                for s in strings:
                    try:
                        decoded = s.decode('utf-8')
                        urls = URL_REGEX.findall(decoded)
                        for u in urls:
                            if u not in unique_urls and not u.startswith("http://schemas.android"):
                                unique_urls.add(u)
                                iocs.append({"ioc_type": "URL", "value": u, "severity": "Medium"})
                        ips = IP_REGEX.findall(decoded)
                        for ip in ips:
                            if ip not in unique_ips and ip != "127.0.0.1" and ip != "0.0.0.0":
                                unique_ips.add(ip)
                                iocs.append({"ioc_type": "IP", "value": ip, "severity": "High"})
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Error extracting IOCs: {e}")

        return iocs

    def get_libraries(self) -> List[Dict[str, Any]]:
        """Detect known SDKs based on dex strings/classes."""
        if not self.apk or not self.dex_files:
            return []
        
        detected_libs = {}
        for dex in self.dex_files:
            for cls in dex.get_classes():
                cls_name = cls.get_name() # e.g. Lcom/google/firebase/Analytics;
                for lib_path, lib_info in KNOWN_LIBRARIES.items():
                    if lib_path in cls_name and lib_path not in detected_libs:
                        detected_libs[lib_path] = lib_info

        # Also add obfuscation detection based on absence of known structure
        # (Simplified: if we see heavily obfuscated packages, we could flag it)

        return list(detected_libs.values())

    def get_yara_matches(self) -> List[Dict[str, Any]]:
        """Run YARA rules on the APK."""
        if not ANDROGUARD_AVAILABLE:
            return []
            
        matches = []
        try:
            # We'll define a simple mock rule string for demonstration, 
            # ideally this should load from a yara_rules/ folder.
            rules_str = """
            rule Malicious_Strings {
                strings:
                    $s1 = "executeShellCommand"
                    $s2 = "su -c"
                    $s3 = "android.intent.action.BOOT_COMPLETED"
                condition:
                    any of them
            }
            """
            rules = yara.compile(source=rules_str)
            yara_matches = rules.match(self.filepath)
            
            for match in yara_matches:
                matched_strings = [str(s[2]) for s in match.strings]
                matches.append({
                    "rule_name": match.rule,
                    "severity": "High",
                    "description": "Matched generic malicious patterns.",
                    "strings_matched": ", ".join(matched_strings),
                    "offset": "0x00",
                    "rule_source": "Internal Ruleset"
                })
        except Exception as e:
            logger.error(f"YARA error: {e}")
            
        return matches
