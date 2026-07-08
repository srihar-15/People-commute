import enum
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class UserRole(str, enum.Enum):
    citizen = "citizen"
    officer = "officer"
    mp = "mp"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="citizen") # Using string to avoid enum matching bugs on sqlite/postgres differences
    phone_number = Column(String(50), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
