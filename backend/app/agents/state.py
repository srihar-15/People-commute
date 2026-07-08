from typing import TypedDict, List, Optional
from uuid import UUID

class AgentState(TypedDict):
    # Grievance metadata
    grievance_id: UUID
    title: str
    description: str
    translated_description: Optional[str]
    original_language: str
    source: str
    citizen_id: UUID
    
    # Coordinates
    latitude: Optional[float]
    longitude: Optional[float]
    
    # AI Decisions
    department_id: Optional[UUID]
    priority: Optional[str] # 'LOW', 'MEDIUM', 'HIGH', 'EMERGENCY'
    priority_score: Optional[float]
    confidence_score: Optional[float]
    master_issue_id: Optional[UUID]
    
    # Audit trail and I/O records
    evidence_urls: List[str]
    audit_notes: List[str]
    
    # Next node indicator
    next_node: str
