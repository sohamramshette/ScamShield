from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database.session import Base

class ThreatCache(Base):
    __tablename__ = "threat_cache"

    cache_key = Column(String, primary_key=True, index=True)
    normalized_input = Column(String, index=True, nullable=False)
    provider = Column(String, index=True, nullable=False)
    raw_response = Column(JSON, nullable=False)
    normalized_response = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), index=True, nullable=False)
