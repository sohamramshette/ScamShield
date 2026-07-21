import hashlib
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.services.providers.base import ThreatProvider, ProviderResult
from app.models.threat_cache import ThreatCache
from app.models.provider_health import ProviderHealth
from app.core.logging import logger

def generate_cache_key(provider_name: str, normalized_input: str) -> str:
    hash_str = f"{provider_name}:{normalized_input}"
    return hashlib.sha256(hash_str.encode()).hexdigest()

class ThreatOrchestrator:
    def __init__(self, db: Session, providers: List[ThreatProvider]):
        self.db = db
        self.providers = providers

    def _check_cache(self, provider_name: str, normalized_input: str) -> Optional[ProviderResult]:
        cache_key = generate_cache_key(provider_name, normalized_input)
        cached = self.db.query(ThreatCache).filter(
            ThreatCache.cache_key == cache_key,
            ThreatCache.expires_at > func.now()
        ).first()

        if cached:
            return ProviderResult(**cached.normalized_response)
        return None

    def _save_cache(self, provider: ThreatProvider, normalized_input: str, result: ProviderResult):
        provider_name = provider.provider_name()
        cache_key = generate_cache_key(provider_name, normalized_input)
        expires_at = datetime.utcnow() + timedelta(hours=provider.cache_ttl_hours)
        
        try:
            cached = self.db.query(ThreatCache).filter(ThreatCache.cache_key == cache_key).first()
            
            if cached:
                cached.raw_response = result.raw_payload if result.raw_payload else {}
                cached.normalized_response = result.model_dump()
                cached.expires_at = expires_at
            else:
                new_cache = ThreatCache(
                    cache_key=cache_key,
                    normalized_input=normalized_input,
                    provider=provider_name,
                    raw_response=result.raw_payload if result.raw_payload else {},
                    normalized_response=result.model_dump(),
                    expires_at=expires_at
                )
                self.db.add(new_cache)
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"[Orchestrator] Error caching result for {provider_name}: {e}")

    def _update_health(self, provider_name: str, is_successful: bool, latency_ms: int, cache_hit: bool = False):
        try:
            health = self.db.query(ProviderHealth).filter(ProviderHealth.provider_name == provider_name).first()
            if not health:
                health = ProviderHealth(provider_name=provider_name, status="Healthy")
                self.db.add(health)
                
            if cache_hit:
                health.cache_hits += 1
            else:
                health.cache_misses += 1
                
            if is_successful:
                health.last_success = func.now()
                health.status = "Healthy"
            else:
                health.last_failure = func.now()
                health.failure_count += 1
                if health.failure_count > 5:
                    health.status = "Degraded"
                    
            # Simple rolling average approximation
            current_latency = health.average_latency_ms or 0
            health.average_latency_ms = (current_latency * 0.9) + (latency_ms * 0.1)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"[Orchestrator] Error updating health for {provider_name}: {e}")

    async def _execute_provider(self, provider: ThreatProvider, method_name: str, payload: str) -> ProviderResult:
        provider_name = provider.provider_name()
        
        # 1. Check Cache
        cached_result = self._check_cache(provider_name, payload)
        if cached_result:
            logger.info(f"[Orchestrator] Cache Hit for {provider_name} -> {payload}")
            self._update_health(provider_name, True, 0, cache_hit=True)
            return cached_result
            
        logger.info(f"[Orchestrator] Cache Miss for {provider_name} -> {payload}. Fetching...")
        
        # 2. Execute Provider (With basic timeout wrapper)
        start_time = datetime.utcnow()
        try:
            method = getattr(provider, method_name)
            # 5-second circuit breaker timeout
            result: ProviderResult = await asyncio.wait_for(method(payload), timeout=5.0)
            latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            result.latency_ms = latency
            
            # 3. Update Health
            self._update_health(provider_name, result.is_successful, latency, cache_hit=False)
            
            # 4. Save Cache (only if successful)
            if result.is_successful:
                self._save_cache(provider, payload, result)
                
            return result
            
        except asyncio.TimeoutError:
            latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self._update_health(provider_name, False, latency, cache_hit=False)
            logger.error(f"[Orchestrator] Timeout executing {provider_name}")
            return ProviderResult(
                provider_name=provider_name,
                trust_weight=provider.trust_weight,
                is_successful=False,
                status="TIMEOUT",
                confidence=0,
                error_message="Timeout execution exceeded 5 seconds",
                latency_ms=latency
            )
        except Exception as e:
            latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self._update_health(provider_name, False, latency, cache_hit=False)
            logger.error(f"[Orchestrator] Error executing {provider_name}: {e}")
            return ProviderResult(
                provider_name=provider_name,
                trust_weight=provider.trust_weight,
                is_successful=False,
                status="ERROR",
                confidence=0,
                error_message=str(e),
                latency_ms=latency
            )

    async def analyze(self, payload_type: str, payload: str) -> List[ProviderResult]:
        """
        Executes all providers concurrently and aggregates results.
        """
        method_name = f"analyze_{payload_type.lower()}"
        
        tasks = []
        for provider in self.providers:
            if hasattr(provider, method_name):
                tasks.append(self._execute_provider(provider, method_name, payload))
                
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out catastrophic asyncio crashes just in case
        valid_results = [r for r in results if isinstance(r, ProviderResult)]
        return valid_results
