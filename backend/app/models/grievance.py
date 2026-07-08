from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from app.core.database import Base

class Grievance(Base):
    __tablename__ = "grievances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    description_embedding = Column(JSONB, nullable=True) # Stored as JSON float array for compatibility
    status = Column(String(50), nullable=False, default="SUBMITTED") # SUBMITTED, HUMAN_REVIEW, CLASSIFIED, DUPLICATE_CLUSTERED, ROUTED, ASSIGNED, RESOLVED, CLOSED
    priority = Column(String(50), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, EMERGENCY
    priority_score = Column(Float, default=0.5)
    
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    assigned_officer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    master_issue_id = Column(UUID(as_uuid=True), ForeignKey("grievances.id", ondelete="SET NULL"), nullable=True)
    explanation_id = Column(UUID(as_uuid=True), ForeignKey("decision_explanations.id", ondelete="SET NULL"), nullable=True)
    
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    source = Column(String(50), nullable=False, default="web") # whatsapp, web
    language = Column(String(10), default="en")
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    sla_deadline = Column(DateTime(timezone=True), nullable=True)
