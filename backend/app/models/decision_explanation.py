from sqlalchemy import Column, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from app.core.database import Base

class DecisionExplanation(Base):
    __tablename__ = "decision_explanations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    classification_reasoning = Column(Text, nullable=False)
    duplicate_similarity_score = Column(Float, nullable=True)
    priority_factors = Column(JSONB, nullable=False) # e.g. {"safety": true, "volume": 1}
    routing_explanation = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    extracted_entities = Column(JSONB, nullable=True) # e.g. {"location": "Ward 4"}
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
