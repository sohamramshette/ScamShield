from sqlalchemy import Column, Integer, String

from app.database.session import Base


class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, nullable=False)
    scan_type = Column(String, nullable=False)  # e.g., 'website', 'qr', 'upi'
    indicator = Column(String, nullable=False)  # e.g., 'SSL Invalid', 'Domain Age'
    severity = Column(String, default="low")  # low, medium, high, critical
    description = Column(String)
    evidence_category = Column(String, default="threat") # threat, reconnaissance, infrastructure, trust
