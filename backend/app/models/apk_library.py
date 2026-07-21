from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.database.session import Base

class APKLibrary(Base):
    __tablename__ = "apk_libraries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("apk_scans.id"), nullable=False)
    
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(String)
    version = Column(String)
    risk = Column(String) # High, Medium, Low, Safe

    scan = relationship("APKScan", back_populates="libraries")
