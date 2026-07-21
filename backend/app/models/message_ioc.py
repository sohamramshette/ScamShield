from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class MessageIOC(Base):
    __tablename__ = "message_iocs"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("message_scans.id", ondelete="CASCADE"))
    
    ioc_type = Column(String, nullable=False) # URL, DOMAIN, PHONE, EMAIL, WALLET, UPI, IP, OTP
    value = Column(String, nullable=False)
    
    severity = Column(String, nullable=True) # High, Medium, Low
    confidence = Column(Integer, nullable=True)
    evidence = Column(JSON, nullable=True)

    message_scan = relationship("MessageScan", back_populates="iocs")
