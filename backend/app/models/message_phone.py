from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class MessagePhone(Base):
    __tablename__ = "message_phones"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("message_scans.id", ondelete="CASCADE"))
    
    number = Column(String, nullable=False)
    country = Column(String, nullable=True)
    reputation = Column(String, nullable=True)
    scam_score = Column(Integer, nullable=True)

    message_scan = relationship("MessageScan", back_populates="phones")
