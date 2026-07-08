from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grievance_id = Column(UUID(as_uuid=True), ForeignKey("grievances.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False) # e.g. 'STATUS_TRANSITION', 'ROUTE_ASSIGNMENT', 'ESCALATION'
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=True)
    rationale = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
