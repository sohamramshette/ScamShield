from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class MessageURL(Base):
    __tablename__ = "message_urls"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("message_scans.id", ondelete="CASCADE"))
    
    url = Column(Text, nullable=False)
    redirect_chain = Column(JSON, nullable=True)
    provider_results = Column(JSON, nullable=True)
    risk_score = Column(Integer, nullable=True)

    message_scan = relationship("MessageScan", back_populates="urls")
