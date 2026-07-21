from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.database.session import Base

class APKPermission(Base):
    __tablename__ = "apk_permissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("apk_scans.id"), nullable=False)
    
    permission = Column(String, nullable=False)
    protection_level = Column(String)
    dangerous = Column(Boolean, default=False)
    justification = Column(String)
    severity = Column(String) # High, Medium, Low

    scan = relationship("APKScan", back_populates="permissions")
