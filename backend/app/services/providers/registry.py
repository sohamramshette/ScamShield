from typing import List
from app.services.providers.base import ThreatProvider
from app.services.providers.offline_rule_engine import OfflineRuleEngineProvider
from app.services.providers.virustotal import VirusTotalProvider
from app.services.providers.google_safe_browsing import GoogleSafeBrowsingProvider
from app.services.providers.whois_provider import WHOISProvider
from app.services.providers.ssl_inspector import SSLInspectorProvider
from app.services.providers.urlscan import URLScanProvider
from app.services.providers.phishtank import PhishTankProvider
from app.services.providers.abuseipdb import AbuseIPDBProvider
from app.core.logging import logger

class ProviderRegistry:
    @staticmethod
    def get_enabled_providers() -> List[ThreatProvider]:
        """
        Instantiates and returns all providers.
        Providers are responsible for evaluating their own settings.*_ENABLED 
        status during instantiation and gracefully returning `is_successful=False`
        if disabled, or we can filter them here if we want to avoid execution overhead.
        
        However, the instruction says "The Orchestrator should simply request 
        ProviderRegistry.get_enabled_providers()".
        """
        all_providers = [
            OfflineRuleEngineProvider(),
            VirusTotalProvider(),
            GoogleSafeBrowsingProvider(),
            WHOISProvider(),
            SSLInspectorProvider(),
            URLScanProvider(),
            PhishTankProvider(),
            AbuseIPDBProvider()
        ]
        
        # We can proactively filter out ones that say they are not enabled.
        # Most of our providers have an `is_enabled` attribute or `health_check` 
        # but to keep it simple and unified:
        active = []
        for provider in all_providers:
            # We can check hasattr for is_enabled (which we added to most network providers)
            # Offline rule engine doesn't have it, we just assume it's always enabled.
            if hasattr(provider, "is_enabled"):
                if getattr(provider, "is_enabled") is True:
                    active.append(provider)
            else:
                active.append(provider)
                
        logger.info(f"ProviderRegistry returning {len(active)} active providers.")
        return active
