from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.database.session import Base

class APKMitre(Base):
    __tablename__ = "apk_mitre_tactics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("apk_scans.id"), nullable=False)
    
    tactic = Column(String, nullable=False)
    technique = Column(String, nullable=False)
    description = Column(String)
    severity = Column(String)

    scan = relationship("APKScan", back_populates="mitre_tactics")
