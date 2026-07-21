from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class EmailURL(Base):
    __tablename__ = "email_urls"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("email_scans.id", ondelete="CASCADE"))
    
    url = Column(String, nullable=False)
    domain = Column(String, nullable=True)
    final_redirect = Column(String, nullable=True)
    
    # Intelligence
    risk_score = Column(Integer, nullable=True)
    confidence = Column(Integer, nullable=True)
    threat_category = Column(String, nullable=True)
    
    # Verdicts
    vt_verdict = Column(String, nullable=True)
    gsb_verdict = Column(String, nullable=True)
    urlscan_verdict = Column(String, nullable=True)
    
    # Context
    ssl_status = Column(String, nullable=True)
    domain_age = Column(Integer, nullable=True)
    
    email_scan = relationship("EmailScan", back_populates="urls")

class EmailHop(Base):
    __tablename__ = "email_hops"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("email_scans.id", ondelete="CASCADE"))
    
    hop_number = Column(Integer, nullable=False)
    server_name = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(String, nullable=True)
    is_suspicious = Column(Boolean, default=False)
    
    email_scan = relationship("EmailScan", back_populates="hops")
