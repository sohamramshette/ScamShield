from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database.session import Base


class QRScan(Base):
    __tablename__ = "qr_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    extracted_data = Column(String, nullable=False)
    data_type = Column(String)  # url, upi, text
    status = Column(String, default="pending")
    risk_score = Column(Integer, nullable=True)
    confidence = Column(Integer, nullable=True)
    ai_explanation = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
