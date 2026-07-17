from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database.session import Base


class WebsiteScan(Base):
    __tablename__ = "website_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, running, completed, failed
    risk_score = Column(Integer, nullable=True)  # 0-100
    confidence = Column(Integer, nullable=True)  # 0-100
    ai_explanation = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
