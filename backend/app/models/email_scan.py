from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class EmailScan(Base):
    __tablename__ = "email_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Identifiers
    sender_address = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    message_id = Column(String, nullable=True)
    reply_to = Column(String, nullable=True)
    return_path = Column(String, nullable=True)
    raw_headers = Column(Text, nullable=True)

    # Flow
    status = Column(String, default="pending")  # pending, running, completed, failed
    processing_time_ms = Column(Integer, nullable=True)
    
    # Auth Status
    spf_status = Column(String, nullable=True)
    dkim_status = Column(String, nullable=True)
    dmarc_status = Column(String, nullable=True)
    
    # Reputation & Intelligence
    sender_reputation = Column(String, nullable=True)
    domain_age = Column(Integer, nullable=True)  # in days
    is_disposable = Column(Boolean, default=False)
    is_scam_domain = Column(Boolean, default=False)
    brand_impersonation_target = Column(String, nullable=True)
    social_engineering_score = Column(Integer, nullable=True)  # 0-100

    # Final Results
    risk_score = Column(Integer, nullable=True)  # 0-100
    confidence = Column(Integer, nullable=True)  # 0-100
    ai_explanation = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Relationships
    attachments = relationship("EmailAttachment", back_populates="email_scan", cascade="all, delete-orphan")
    hops = relationship("EmailHop", back_populates="email_scan", cascade="all, delete-orphan")
    urls = relationship("EmailURL", back_populates="email_scan", cascade="all, delete-orphan")
