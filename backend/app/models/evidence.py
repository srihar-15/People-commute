from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from app.core.database import Base

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id = Column(UUID(as_uuid=True), ForeignKey("grievances.id", ondelete="CASCADE"), nullable=False)
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_url = Column(String(1024), nullable=False)
    notes = Column(Text, nullable=True)
    type = Column(String(50), nullable=False) # 'intake_evidence' | 'closure_proof'
    vision_ocr_text = Column(Text, nullable=True)
    verification_report = Column(JSONB, nullable=True) # Result from before/after image validation
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
