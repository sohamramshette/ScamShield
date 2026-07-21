from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class EmailAttachment(Base):
    __tablename__ = "email_attachments"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("email_scans.id", ondelete="CASCADE"))
    
    filename = Column(String, nullable=True)
    extension = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    sha256 = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    
    # Flags
    dangerous_extension = Column(Boolean, default=False)
    double_extension = Column(Boolean, default=False)
    is_executable = Column(Boolean, default=False)
    has_macro = Column(Boolean, default=False)
    is_archive = Column(Boolean, default=False)
    is_password_protected = Column(Boolean, default=False)
    
    # AV
    vt_detection_ratio = Column(String, nullable=True)
    vt_first_seen = Column(String, nullable=True)
    risk_level = Column(String, nullable=True) # Safe, Low, Medium, High, Critical
    
    email_scan = relationship("EmailScan", back_populates="attachments")
