from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.analytics import get_constituency_kpis, recalculate_all_wards
from app.services.rag import generate_policy_response
from app.schemas import PolicyQuery, PolicyResponse
from app.models.health import ConstituencyHealthIndex

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/kpi")
def get_kpis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns high-level KPI counts, averages, and health breakdowns.
    MP and Admin roles only.
    """
    if current_user.role != "mp" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Authorized personnel only")
        
    return get_constituency_kpis(db)

@router.get("/health-index")
def get_ward_health_indices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns latest health index snapshots for all wards.
    """
    if current_user.role != "mp" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Authorized personnel only")
        
    wards = ["Ward 1 (Vasant Nagar)", "Ward 2 (Ganesh Nagar)", "Ward 3 (Subhash Nagar)", "Ward 4 (Bhimrao Colony)", "Ward 5 (Shastri Nagar)"]
    result = []
    
    for w in wards:
        latest = db.query(ConstituencyHealthIndex).filter_by(ward_id=w).order_by(ConstituencyHealthIndex.computed_at.desc()).first()
        if latest:
            result.append({
                "ward_id": latest.ward_id,
                "water_score": latest.water_score,
                "roads_score": latest.roads_score,
                "electricity_score": latest.electricity_score,
                "education_score": latest.education_score,
                "healthcare_score": latest.healthcare_score,
                "sanitation_score": latest.sanitation_score,
                "safety_score": latest.safety_score,
                "overall_health_index": latest.overall_health_index,
                "computed_at": latest.computed_at.isoformat()
            })
            
    return result

@router.post("/recalculate")
def trigger_recalculation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Forces recalculation of health scores for all wards.
    """
    if current_user.role != "admin" and current_user.role != "mp":
        raise HTTPException(status_code=403, detail="Access denied")
        
    recalculate_all_wards(db)
    return {"message": "Constituency Health Index successfully updated."}

@router.post("/policy-rag", response_model=PolicyResponse)
def policy_assistant_chat(
    payload: PolicyQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RAG-based Governance Intelligence Agent chat.
    Answers natural language queries strictly referencing versioned policies and plans.
    Also handles action commands (e.g. Escalate, Allot).
    """
    if current_user.role != "mp" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Authorized personnel only")
        
    query_lower = payload.query.lower()
    
    # 1. Action Parser (Executive Agent Upgrade)
    import re
    # Match: "escalate grievance 1234 to emergency" or "escalate 1234"
    escalate_match = re.search(r'escalate\s+(?:grievance|issue|task)?\s*([a-f0-9\-]+)', query_lower)
    if escalate_match:
        from app.api.grievances import mp_manual_escalate
        from uuid import UUID
        g_id = escalate_match.group(1)
        try:
            mp_manual_escalate(UUID(g_id), priority="EMERGENCY", hours_to_resolve=4, current_user=current_user, db=db)
            
            from app.models.audit import AuditLog
            audit = AuditLog(
                grievance_id=UUID(g_id),
                user_id=current_user.id,
                action="PolicyIntelligenceAgent",
                old_status=None,
                new_status=None,
                rationale=f"Executive Action: Escalated grievance via Policy NLP interface: '{payload.query}'."
            )
            db.add(audit)
            db.commit()
            
            return {"answer": f"✅ Executed Action: Escalated grievance {g_id[:8]} to EMERGENCY status with a 4-hour SLA.", "sources": []}
        except Exception as e:
            return {"answer": f"❌ Failed to escalate: {str(e)}", "sources": []}

    # Match: "allot grievance 1234 to water"
    allot_match = re.search(r'allot\s+(?:grievance|issue|task)?\s*([a-f0-9\-]+)\s+(?:to\s+)?([a-z]+)', query_lower)
    if allot_match:
        from app.api.grievances import admin_manual_route
        from app.models import Department
        from uuid import UUID
        g_id = allot_match.group(1)
        dept_str = allot_match.group(2)
        
        # Find matching department
        dept = db.query(Department).filter(Department.name.ilike(f"%{dept_str}%") | Department.code.ilike(f"%{dept_str}%")).first()
        if dept:
            try:
                admin_manual_route(UUID(g_id), department_id=dept.id, priority="HIGH", current_user=current_user, db=db)
                
                from app.models.audit import AuditLog
                audit = AuditLog(
                    grievance_id=UUID(g_id),
                    user_id=current_user.id,
                    action="PolicyIntelligenceAgent",
                    old_status=None,
                    new_status=None,
                    rationale=f"Executive Action: Re-routed grievance via Policy NLP interface to '{dept.name}': '{payload.query}'."
                )
                db.add(audit)
                db.commit()
                
                return {"answer": f"✅ Executed Action: Allotted grievance {g_id[:8]} to {dept.name}.", "sources": []}
            except Exception as e:
                return {"answer": f"❌ Failed to allot: {str(e)}", "sources": []}
        else:
            return {"answer": f"❌ Could not find a department matching '{dept_str}'.", "sources": []}

    # 2. Standard RAG Chatbot
    response = generate_policy_response(db, query=payload.query, limit=3)
    return response
