from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "citizen" # 'citizen' | 'officer' | 'mp' | 'admin'
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str
    email: str
    user_id: UUID

class UserOut(BaseModel):
    id: UUID
    email: Optional[str]
    full_name: str
    role: str
    phone_number: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Grievance Schemas ---
class GrievanceCreate(BaseModel):
    title: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: str = "web" # 'web' | 'whatsapp'
    language: str = "en"
    evidence_url: Optional[str] = None

class EvidenceOut(BaseModel):
    id: UUID
    media_url: str
    notes: Optional[str]
    type: str
    verification_report: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DecisionExplanationOut(BaseModel):
    classification_reasoning: str
    duplicate_similarity_score: Optional[float]
    priority_factors: Dict[str, Any]
    routing_explanation: str
    confidence_score: float
    extracted_entities: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class GrievanceOut(BaseModel):
    id: UUID
    title: str
    description: str
    status: str
    priority: str
    priority_score: float
    citizen_id: UUID
    department_id: Optional[UUID]
    assigned_officer_id: Optional[UUID]
    master_issue_id: Optional[UUID]
    latitude: Optional[float]
    longitude: Optional[float]
    source: str
    language: str
    created_at: datetime
    resolved_at: Optional[datetime]
    sla_deadline: Optional[datetime]
    
    class Config:
        from_attributes = True

class AuditLogOut(BaseModel):
    id: UUID
    action: str
    old_status: Optional[str]
    new_status: Optional[str]
    rationale: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class GrievanceDetailOut(GrievanceOut):
    explanation: Optional[DecisionExplanationOut] = None
    evidence: List[EvidenceOut] = []
    audit_logs: List[AuditLogOut] = []
    
    class Config:
        from_attributes = True

class ResolutionSubmit(BaseModel):
    evidence_url: str
    notes: str = ""

# --- RAG Policy Schemas ---
class PolicyQuery(BaseModel):
    query: str

class PolicyResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
