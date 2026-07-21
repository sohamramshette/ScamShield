from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class MessageScan(Base):
    __tablename__ = "message_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Input Data
    platform = Column(String, index=True) # SMS, WhatsApp
    sender = Column(String, nullable=True)
    receiver = Column(String, nullable=True)
    language = Column(String, nullable=True)
    message_text = Column(Text, nullable=False)
    
    # Performance
    processing_time_ms = Column(Integer, nullable=True)

    # Final Results
    scam_type = Column(String, nullable=True)
    social_engineering_score = Column(Integer, nullable=True) # 0-100
    
    # Confidence breakdown
    ocr_confidence = Column(Integer, nullable=True)
    threat_intel_confidence = Column(Integer, nullable=True)
    language_confidence = Column(Integer, nullable=True)
    reputation_confidence = Column(Integer, nullable=True)
    rule_engine_confidence = Column(Integer, nullable=True)
    
    confidence = Column(Integer, nullable=True) # Overall
    risk_score = Column(Integer, nullable=True) # 0-100
    
    ai_summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Relationships
    urls = relationship("MessageURL", back_populates="message_scan", cascade="all, delete-orphan")
    phones = relationship("MessagePhone", back_populates="message_scan", cascade="all, delete-orphan")
    iocs = relationship("MessageIOC", back_populates="message_scan", cascade="all, delete-orphan")
