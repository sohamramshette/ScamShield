from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import uuid

from app.database.session import Base

class APKCertificate(Base):
    __tablename__ = "apk_certificates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("apk_scans.id"), nullable=False)
    
    issuer = Column(String)
    subject = Column(String)
    fingerprint = Column(String) # SHA-256
    signature_algorithm = Column(String)
    expired = Column(Boolean, default=False)
    self_signed = Column(Boolean, default=False)
    trust_level = Column(String) # Trusted, Untrusted, Unknown
    risk_level = Column(String) # High, Medium, Low

    scan = relationship("APKScan", back_populates="certificates")
