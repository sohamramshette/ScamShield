from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any


# Token
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    email: Optional[str] = None


# User
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Threat Indicator
class ThreatIndicatorSchema(BaseModel):
    indicator: str
    severity: str
    description: Optional[str] = None
    evidence_category: str = "threat"

    class Config:
        from_attributes = True


# Providers
class ProviderSchema(BaseModel):
    name: str
    status: str
    result: str
    contribution: int
    confidence: int
    latency_ms: int

# Scans
class ScanBase(BaseModel):
    status: str
    risk_score: Optional[int]
    confidence: Optional[int]
    analysis_mode: Optional[str] = "LIVE"
    providers: List[ProviderSchema] = []
    ai_explanation: Optional[str]
    recommendations: Optional[str]
    created_at: datetime


class WebsiteScanResponse(ScanBase):
    id: int
    url: str
    threat_indicators: List[ThreatIndicatorSchema] = []

    class Config:
        from_attributes = True

class QRScanResponse(ScanBase):
    id: int
    extracted_data: str
    threat_indicators: List[ThreatIndicatorSchema] = []

    class Config:
        from_attributes = True

class UPIScanResponse(ScanBase):
    id: str
    upi_id: str
    threat_indicators: List[ThreatIndicatorSchema] = []

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    target: str  # Can be URL, QR data, or UPI ID
