from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.session import Base

class APKScan(Base):
    __tablename__ = "apk_scans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # APK Info
    filename = Column(String)
    package_name = Column(String)
    version = Column(String)
    version_code = Column(Integer)
    min_sdk = Column(Integer)
    target_sdk = Column(Integer)
    compile_sdk = Column(Integer)
    size_bytes = Column(Integer)
    architecture = Column(String)
    dex_count = Column(Integer)
    sha256 = Column(String)
    manifest_json = Column(String) # Stored as JSON string

    # Security Breakdown
    permission_risk = Column(Integer, default=0)
    certificate_risk = Column(Integer, default=0)
    manifest_risk = Column(Integer, default=0)
    component_risk = Column(Integer, default=0)
    yara_risk = Column(Integer, default=0)
    network_risk = Column(Integer, default=0)
    code_risk = Column(Integer, default=0)
    
    risk_score = Column(Integer, default=0)
    confidence = Column(Integer, default=0)
    
    # Similarity Engine
    similarity_score = Column(Integer, default=0)
    closest_sample_id = Column(String)

    # AI Investigation
    ai_family = Column(String)
    ai_summary = Column(String)
    ai_behaviour = Column(String)
    ai_impact = Column(String)
    ai_actions = Column(String)
    
    malware_family = Column(String) # Kept for backward compatibility or direct assignment
    recommendations = Column(String) # Kept for backward compatibility

    # Relationships
    permissions = relationship("APKPermission", back_populates="scan", cascade="all, delete-orphan")
    components = relationship("APKComponent", back_populates="scan", cascade="all, delete-orphan")
    certificates = relationship("APKCertificate", back_populates="scan", cascade="all, delete-orphan")
    iocs = relationship("APKIOC", back_populates="scan", cascade="all, delete-orphan")
    libraries = relationship("APKLibrary", back_populates="scan", cascade="all, delete-orphan")
    yara_matches = relationship("APKYaraMatch", back_populates="scan", cascade="all, delete-orphan")
    mitre_tactics = relationship("APKMitre", back_populates="scan", cascade="all, delete-orphan")
