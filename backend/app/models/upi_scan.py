from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database.session import Base


class UPIScan(Base):
    __tablename__ = "upi_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    upi_id = Column(String, nullable=False)
    merchant_name = Column(String, nullable=True)
    status = Column(String, default="pending")
    risk_score = Column(Integer, nullable=True)
    confidence = Column(Integer, nullable=True)
    ai_explanation = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
