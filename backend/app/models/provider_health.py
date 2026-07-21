from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.sql import func
from app.database.session import Base

class ProviderHealth(Base):
    __tablename__ = "provider_health"

    provider_name = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    average_latency_ms = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)
    failure_count = Column(Integer, default=0)
    last_success = Column(DateTime(timezone=True), nullable=True)
    last_failure = Column(DateTime(timezone=True), nullable=True)
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)
