from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.database.session import Base

class APKIOC(Base):
    __tablename__ = "apk_iocs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("apk_scans.id"), nullable=False)
    
    ioc_type = Column(String, nullable=False) # URL, Domain, IP, Wallet, Email, API Key, Firebase, AWS Keys, etc.
    value = Column(String, nullable=False)
    severity = Column(String) # High, Medium, Low

    scan = relationship("APKScan", back_populates="iocs")
