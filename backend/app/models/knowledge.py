from sqlalchemy import Column, String, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from app.core.database import Base

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content_chunk = Column(Text, nullable=False)
    embedding = Column(JSONB, nullable=True) # Stored as JSON float array for compatibility
    source_uri = Column(String(512), nullable=False)
    version = Column(String(50), nullable=False) # e.g. '1.0.0'
    publication_date = Column(Date, nullable=False)
    metadata_info = Column(JSONB, nullable=True) # Renamed to metadata_info to avoid SQLAlchemy metadata collision
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
