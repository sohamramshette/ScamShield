from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel
import httpx
import asyncio

class ProviderResult(BaseModel):
    provider_name: str
    trust_weight: float
    is_successful: bool
    status: str = "ONLINE"
    confidence: int = 100
    indicators: List[Dict] = []
    raw_payload: Optional[Dict] = None
    latency_ms: int = 0
    error_message: Optional[str] = None

class ThreatProvider(ABC):
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique identifier of the provider."""
        pass

    @property
    @abstractmethod
    def trust_weight(self) -> float:
        """Returns the confidence multiplier for this provider (e.g., 1.0, 0.45)."""
        pass

    @property
    def cache_ttl_hours(self) -> int:
        """Number of hours to cache successful results"""
        return 24

    @abstractmethod
    async def analyze_url(self, url: str) -> ProviderResult:
        """Analyzes a URL and returns a unified ProviderResult."""
        pass

    @abstractmethod
    async def analyze_ip(self, ip: str) -> ProviderResult:
        """Analyzes an IP address and returns a unified ProviderResult."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Pings the provider to check basic availability."""
        pass
