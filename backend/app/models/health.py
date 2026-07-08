from sqlalchemy import Column, Float, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class ConstituencyHealthIndex(Base):
    __tablename__ = "constituency_health_index"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ward_id = Column(String(50), nullable=False)
    roads_score = Column(Float, default=100.0)
    water_score = Column(Float, default=100.0)
    electricity_score = Column(Float, default=100.0)
    education_score = Column(Float, default=100.0)
    healthcare_score = Column(Float, default=100.0)
    sanitation_score = Column(Float, default=100.0)
    safety_score = Column(Float, default=100.0)
    overall_health_index = Column(Float, default=100.0)
    computed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
