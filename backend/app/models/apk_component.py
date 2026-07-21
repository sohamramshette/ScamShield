from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.database.session import Base

class APKComponent(Base):
    __tablename__ = "apk_components"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("apk_scans.id"), nullable=False)
    
    component_type = Column(String, nullable=False) # Activity, Service, Receiver, Provider
    name = Column(String, nullable=False)
    exported = Column(Boolean, default=False)
    permission = Column(String)
    enabled = Column(Boolean, default=True)

    scan = relationship("APKScan", back_populates="components")
