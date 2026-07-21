from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.database.session import Base

class APKYaraMatch(Base):
    __tablename__ = "apk_yara_matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("apk_scans.id"), nullable=False)
    
    rule_name = Column(String, nullable=False)
    severity = Column(String)
    description = Column(String)
    strings_matched = Column(String)
    offset = Column(String)
    rule_source = Column(String)

    scan = relationship("APKScan", back_populates="yara_matches")
