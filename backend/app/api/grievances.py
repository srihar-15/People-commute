from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import Grievance, User, Evidence, AuditLog, Department, DecisionExplanation
from app.schemas import (
    GrievanceCreate, GrievanceOut, GrievanceDetailOut,
    ResolutionSubmit, UserOut
)
from app.agents.graph import execute_agent_workflow
from app.services.assurance import run_resolution_assurance
from app.services.ai import ai_service
from app.services.rag import retrieve_context
from app.core.websocket_manager import manager
import datetime
import numpy as np
from uuid import UUID
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/grievances", tags=["grievances"])

# Helper to run LangGraph asynchronously and broadcast live status
def run_agent_in_background(g_id: UUID, title: str, description: str, language: str, source: str, citizen_id: UUID):
    try:
        execute_agent_workflow(
            grievance_id=g_id,
            title=title,
            description=description,
            language=language,
            source=source,
            citizen_id=citizen_id
        )
        # Broadcast completed status
        manager.broadcast_all_sync({
            "event": "GRIEVANCE_UPDATED",
            "grievance_id": str(g_id),
            "status": "ROUTED",
            "message": f"Grievance '{title}' automatically routed to department queue."
        })
    except Exception as e:
        print(f"Error executing agent in background: {e}")

@router.post("/", response_model=GrievanceOut, status_code=status.HTTP_201_CREATED)
def file_grievance(
    grievance_in: GrievanceCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits a new grievance.
    Creates DB record and starts the asynchronous LangGraph intake & classification pipeline.
    """
    # Create grievance
    new_grievance = Grievance(
        title=grievance_in.title,
        description=grievance_in.description,
        status="SUBMITTED",
        priority="MEDIUM",
        citizen_id=current_user.id,
        latitude=grievance_in.latitude,
        longitude=grievance_in.longitude,
        source=grievance_in.source,
        language=grievance_in.language
    )
    db.add(new_grievance)
    db.flush()
    
    # Save intake evidence if url is provided
    if grievance_in.evidence_url:
        evidence = Evidence(
            grievance_id=new_grievance.id,
            uploader_id=current_user.id,
            media_url=grievance_in.evidence_url,
            type="intake_evidence",
            notes="Uploaded during grievance intake."
        )
        db.add(evidence)
        
    # Log initial submit audit
    audit = AuditLog(
        grievance_id=new_grievance.id,
        user_id=current_user.id,
        action="SUBMIT",
        old_status=None,
        new_status="SUBMITTED",
        rationale=f"Grievance filed via {grievance_in.source} in language code '{grievance_in.language}'."
    )
    db.add(audit)
    db.commit()
    db.refresh(new_grievance)
    
    # Queue LangGraph Agent processing in background thread
    background_tasks.add_task(
        run_agent_in_background,
        new_grievance.id,
        new_grievance.title,
        new_grievance.description,
        new_grievance.language,
        new_grievance.source,
        current_user.id
    )
    
    # Notify dashboard of new submittal
    background_tasks.add_task(
        manager.broadcast_all_sync,
        {
            "event": "GRIEVANCE_SUBMITTED",
            "grievance_id": str(new_grievance.id),
            "title": new_grievance.title,
            "status": "SUBMITTED"
        }
    )
    
    return new_grievance

from pydantic import BaseModel
class WhatsAppPayload(BaseModel):
    message: Optional[str] = None
    media_url: Optional[str] = None
    content_type: Optional[str] = None

@router.post("/whatsapp")
def handle_whatsapp_message(
    payload: WhatsAppPayload,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Runs citizen input through a stateful LangGraph conversation flow.
    Gathers missing details (category, description, location) dynamically.
    """
    from app.agents.conversational_agent import citizen_chat_graph
    
    config = {"configurable": {"thread_id": str(current_user.id)}}
    state = citizen_chat_graph.get_state(config)
    
    if not state or not state.values:
        messages = []
        category = None
        location = None
        description = None
        duration = None
        accidents_caused = None
        image_url = None
        is_complete = False
    else:
        messages = state.values.get("messages", [])
        category = state.values.get("category")
        location = state.values.get("location")
        description = state.values.get("description")
        duration = state.values.get("duration")
        accidents_caused = state.values.get("accidents_caused")
        image_url = state.values.get("image_url")
        is_complete = state.values.get("is_complete", False)

    # Append input details
    if payload.media_url:
        image_url = payload.media_url
        messages.append({"role": "user", "content": f"[Uploaded Evidence Photo: {payload.media_url}]"})
    elif payload.message:
        messages.append({"role": "user", "content": payload.message})

    # Prepare input state
    input_state = {
        "user_id": str(current_user.id),
        "messages": messages,
        "category": category,
        "location": location,
        "description": description,
        "duration": duration,
        "accidents_caused": accidents_caused,
        "image_url": image_url,
        "is_complete": is_complete,
        "followup_question": "",
        "grievance_id": None
    }

    # Run LangGraph StateGraph execution
    citizen_chat_graph.update_state(config, input_state)
    result = citizen_chat_graph.invoke(None, config)

    if result.get("is_complete"):
        # File the official grievance in DB
        title_prefix = result.get("category") or "General"
        g_in = GrievanceCreate(
            title=f"{title_prefix.capitalize()} Issue Reported",
            description=f"{result.get('description') or 'No description provided'}.\nLocation: {result.get('location')}.\nDuration: {result.get('duration') or 'Not specified'}.\nImmediate Hazards: {result.get('accidents_caused') or 'None'}.",
            latitude=16.5062,
            longitude=80.6480,
            source="WHATSAPP",
            language="en",
            evidence_url=result.get("image_url")
        )
        new_g = file_grievance(g_in, background_tasks, current_user, db)
        
        # Clear checkpoint history for user
        citizen_chat_graph.update_state(config, {
            "messages": [],
            "category": None,
            "location": None,
            "description": None,
            "duration": None,
            "accidents_caused": None,
            "image_url": None,
            "is_complete": False,
            "followup_question": ""
        })
        
        return {
            "reply": f"Dhanyavaad Rameshji 🙏 I have registered your grievance under Ticket ID: {str(new_g.id)[:8]}. Our system has routed it to the corresponding Department queue."
        }
    else:
        # Get question
        reply = result.get("followup_question") or "Could you please specify the exact location or landmark near the issue?"
        messages.append({"role": "assistant", "content": reply})
        citizen_chat_graph.update_state(config, {"messages": messages})
        return {"reply": reply}

@router.get("/", response_model=List[GrievanceOut])
def list_grievances(
    status_filter: Optional[str] = None,
    dept_filter: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists grievances based on RBAC roles:
    - Citizen: see own filed grievances.
    - Officer: see grievances in department queue (ROUTED or ASSIGNED to them).
    - MP/Admin: see all grievances.
    """
    query = db.query(Grievance)
    
    if current_user.role == "citizen":
        query = query.filter_by(citizen_id=current_user.id)
    elif current_user.role == "officer":
        # Officer belongs to a department. Let's find the department they lead
        dept = db.query(Department).filter_by(head_officer_id=current_user.id).first()
        if dept:
            # Query routed to their department, or assigned to them, or resolved by them
            query = query.filter(
                Grievance.department_id == dept.id,
                Grievance.status.in_(["ROUTED", "ASSIGNED", "RESOLVED", "CLOSED"])
            )
        else:
            # Fallback
            query = query.filter(Grievance.assigned_officer_id == current_user.id)
            
    # Apply standard query filters
    if status_filter:
        query = query.filter(Grievance.status == status_filter)
    if dept_filter:
        query = query.filter(Grievance.department_id == dept_filter)
        
    return query.order_by(Grievance.created_at.desc()).all()

@router.get("/{id}", response_model=GrievanceDetailOut)
def get_grievance_detail(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grievance = db.query(Grievance).filter_by(id=id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    # Check permissions
    if current_user.role == "citizen" and grievance.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this grievance")
        
    # Retrieve explanation
    explanation = None
    if grievance.explanation_id:
        explanation = db.query(DecisionExplanation).filter_by(id=grievance.explanation_id).first()
        
    # Retrieve evidence
    evidence = db.query(Evidence).filter_by(grievance_id=id).order_by(Evidence.created_at.desc()).all()
    
    # Retrieve audit logs
    audit_logs = db.query(AuditLog).filter_by(grievance_id=id).order_by(AuditLog.timestamp.asc()).all()
    
    # Map detail shape
    return {
        "id": grievance.id,
        "title": grievance.title,
        "description": grievance.description,
        "status": grievance.status,
        "priority": grievance.priority,
        "priority_score": grievance.priority_score,
        "citizen_id": grievance.citizen_id,
        "department_id": grievance.department_id,
        "assigned_officer_id": grievance.assigned_officer_id,
        "master_issue_id": grievance.master_issue_id,
        "latitude": grievance.latitude,
        "longitude": grievance.longitude,
        "source": grievance.source,
        "language": grievance.language,
        "created_at": grievance.created_at,
        "resolved_at": grievance.resolved_at,
        "sla_deadline": grievance.sla_deadline,
        "explanation": explanation,
        "evidence": evidence,
        "audit_logs": audit_logs
    }

@router.post("/{id}/accept", response_model=GrievanceOut)
def accept_grievance(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Officer pulls/accepts a task from their Department Queue.
    """
    if current_user.role != "officer":
        raise HTTPException(status_code=403, detail="Only department officers can accept tasks")
        
    grievance = db.query(Grievance).filter_by(id=id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    if grievance.status != "ROUTED":
        raise HTTPException(status_code=400, detail="Grievance is not in the ROUTED queue")
        
    # Check if officer department matches
    dept = db.query(Department).filter_by(head_officer_id=current_user.id).first()
    if not dept or grievance.department_id != dept.id:
        raise HTTPException(status_code=400, detail="Officer does not belong to the routed department")
        
    old_status = grievance.status
    grievance.status = "ASSIGNED"
    grievance.assigned_officer_id = current_user.id
    
    audit = AuditLog(
        grievance_id=id,
        user_id=current_user.id,
        action="OFFICER_ACCEPT",
        old_status=old_status,
        new_status="ASSIGNED",
        rationale=f"Accepted by officer: {current_user.full_name}."
    )
    db.add(audit)
    db.commit()
    db.refresh(grievance)
    
    # Broadcast updates to WebSockets
    manager.broadcast_all_sync({
        "event": "GRIEVANCE_UPDATED",
        "grievance_id": str(id),
        "status": "ASSIGNED",
        "assigned_to": current_user.full_name
    })
    
    return grievance

@router.post("/{id}/resolve")
def resolve_grievance(
    id: UUID,
    resolution: ResolutionSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Officer submits proof of repair. Triggers image-based Resolution Assurance Agent.
    """
    if current_user.role != "officer":
        raise HTTPException(status_code=403, detail="Only officers can resolve grievances")
        
    result = run_resolution_assurance(
        db=db,
        grievance_id=id,
        officer_id=current_user.id,
        proof_url=resolution.evidence_url,
        notes=resolution.notes
    )
    
    # Broadcast updates to WebSockets
    if result["success"]:
        manager.broadcast_all_sync({
            "event": "GRIEVANCE_UPDATED",
            "grievance_id": str(id),
            "status": "RESOLVED",
            "message": "AI Verification passed. Awaiting citizen confirmation."
        })
    else:
        manager.broadcast_all_sync({
            "event": "GRIEVANCE_UPDATED",
            "grievance_id": str(id),
            "status": "ASSIGNED",
            "message": f"AI Verification failed: {result['message']}"
        })
        
    return result

@router.post("/{id}/confirm", response_model=GrievanceOut)
def confirm_closure(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Citizen confirms resolution. Closes grievance.
    """
    grievance = db.query(Grievance).filter_by(id=id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    if current_user.role != "admin" and grievance.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the filing citizen can close this grievance")
        
    if grievance.status != "RESOLVED":
        raise HTTPException(status_code=400, detail="Grievance has not been marked resolved yet")
        
    old_status = grievance.status
    grievance.status = "CLOSED"
    grievance.resolved_at = datetime.datetime.utcnow()
    
    audit = AuditLog(
        grievance_id=id,
        user_id=current_user.id,
        action="CitizenConfirmationAgent",
        old_status=old_status,
        new_status="CLOSED",
        rationale="Citizen confirmed closure. Grievance successfully resolved and audited."
    )
    db.add(audit)
    db.commit()
    db.refresh(grievance)
    
    # Broadcast update
    manager.broadcast_all_sync({
        "event": "GRIEVANCE_UPDATED",
        "grievance_id": str(id),
        "status": "CLOSED"
    })
    
    return grievance

@router.post("/{id}/reject", response_model=GrievanceOut)
def reject_resolution(
    id: UUID,
    reopen_notes: str = "Citizen rejected closure.",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Citizen rejects resolution. Reopens grievance and raises priority.
    """
    grievance = db.query(Grievance).filter_by(id=id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    if grievance.citizen_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only the filing citizen can reject resolution")
        
    if grievance.status != "RESOLVED":
        raise HTTPException(status_code=400, detail="Grievance is not in RESOLVED state")
        
    old_status = grievance.status
    grievance.status = "ASSIGNED"
    
    # Escalate priority
    grievance.priority = "HIGH" if grievance.priority == "MEDIUM" else "EMERGENCY"
    grievance.priority_score = min(grievance.priority_score + 0.15, 1.0)
    
    # Shorten SLA deadline
    grievance.sla_deadline = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    
    audit = AuditLog(
        grievance_id=id,
        user_id=current_user.id,
        action="CitizenConfirmationAgent",
        old_status=old_status,
        new_status="ASSIGNED",
        rationale=f"Citizen disputed repair: {reopen_notes}. Priority boosted to {grievance.priority}. Urgent SLA reset."
    )
    db.add(audit)
    db.commit()
    db.refresh(grievance)
    
    # Broadcast update
    manager.broadcast_all_sync({
        "event": "GRIEVANCE_UPDATED",
        "grievance_id": str(id),
        "status": "ASSIGNED",
        "priority": grievance.priority,
        "message": "Citizen disputed the resolution. Grievance reopened and escalated!"
    })
    
    return grievance

@router.post("/{id}/admin-review", response_model=GrievanceOut)
def admin_manual_route(
    id: UUID,
    department_id: UUID,
    priority: str = "MEDIUM",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin manually overrides routing for low-confidence or disputed issues.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin authorization required")
        
    grievance = db.query(Grievance).filter_by(id=id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    old_status = grievance.status
    grievance.status = "ROUTED"
    grievance.department_id = department_id
    grievance.priority = priority
    
    dept = db.query(Department).filter_by(id=department_id).first()
    sla_hours = dept.sla_hours if dept else 48
    grievance.sla_deadline = datetime.datetime.utcnow() + datetime.timedelta(hours=sla_hours)
    
    audit = AuditLog(
        grievance_id=id,
        user_id=current_user.id,
        action="ADMIN_ROUTE",
        old_status=old_status,
        new_status="ROUTED",
        rationale=f"Admin manually resolved classification routing. Dispatched to queue: {dept.name if dept else 'Unknown'}."
    )
    db.add(audit)
    db.commit()
    db.refresh(grievance)
    
    # Broadcast update
    manager.broadcast_all_sync({
        "event": "GRIEVANCE_UPDATED",
        "grievance_id": str(id),
        "status": "ROUTED",
        "message": "Admin manually classified and routed the grievance."
    })
    
    return grievance

@router.post("/{id}/mp-escalate", response_model=GrievanceOut)
def mp_manual_escalate(
    id: UUID,
    priority: str = "EMERGENCY",
    hours_to_resolve: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    MP Governance oversight action. Can override deadline and raise urgency levels.
    """
    if current_user.role != "mp" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="MP or Admin authorization required")
        
    grievance = db.query(Grievance).filter_by(id=id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    grievance.priority = priority
    grievance.priority_score = 0.98 if priority == "EMERGENCY" else 0.85
    grievance.sla_deadline = datetime.datetime.utcnow() + datetime.timedelta(hours=hours_to_resolve)
    
    audit = AuditLog(
        grievance_id=id,
        user_id=current_user.id,
        action="MP_ESCALATION",
        old_status=grievance.status,
        new_status=grievance.status,
        rationale=f"MP Dr. Chandrababu manually escalated issue to {priority} with a strict {hours_to_resolve}-hour deadline."
    )
    db.add(audit)
    db.commit()
    db.refresh(grievance)
    
    # Broadcast update
    manager.broadcast_all_sync({
        "event": "GRIEVANCE_UPDATED",
        "grievance_id": str(id),
        "priority": priority,
        "message": f"MP Escalated this grievance! Critical {hours_to_resolve}-hour deadline set."
    })
    
    return grievance

@router.get("/{id}/assistant")
def get_officer_ai_assistant(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Officer Assistant Agent utility:
    Provides relevant SOP references, likely resolution steps, and pulls historically
    similar resolved cases using Python-based cosine vector search.
    """
    if current_user.role != "officer" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Authorized personnel only")
        
    grievance = db.query(Grievance).filter_by(id=id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    # Get SOP references
    dept = db.query(Department).filter_by(id=grievance.department_id).first()
    category = dept.code if dept else None
    
    sops = retrieve_context(db, query=grievance.description, limit=2, category_filter=category)
    
    # Log OfficerAssistantAgent reading context
    audit_assist = AuditLog(
        grievance_id=id,
        user_id=current_user.id,
        action="OfficerAssistantAgent",
        old_status=grievance.status,
        new_status=grievance.status,
        rationale=f"Officer AI Assistant retrieved {len(sops)} applicable SOP reference(s) for department: {category}."
    )
    db.add(audit_assist)
    db.commit()
    
    # Search similar resolved cases
    resolved_cases = db.query(Grievance).filter(
        Grievance.id != id,
        Grievance.status == "CLOSED",
        Grievance.description_embedding.isnot(None)
    ).all()
    
    similar_cases = []
    if grievance.description_embedding:
        q_vec = np.array(grievance.description_embedding)
        for g in resolved_cases:
            g_vec = np.array(g.description_embedding)
            similarity = float(np.dot(q_vec, g_vec))
            if similarity > 0.65: # Threshold
                # Retrieve resolution notes
                closure_ev = db.query(Evidence).filter_by(grievance_id=g.id, type="closure_proof").first()
                similar_cases.append({
                    "id": str(g.id),
                    "title": g.title,
                    "similarity": round(similarity, 2),
                    "resolution_notes": closure_ev.notes if closure_ev else "Resolution completed."
                })
        # Sort by similarity descending
        similar_cases.sort(key=lambda x: x["similarity"], reverse=True)
        
    return {
        "suggested_sops": sops,
        "similar_cases": similar_cases[:3],
        "likely_steps": [
            "1. Inspect site and verify details outlined in the citizen description.",
            "2. Ensure appropriate materials (clamps for pipes, hot-mix aggregates for road patches) are available.",
            "3. Execute repairs adhering to the retrieved SOP specifications.",
            "4. Take a clear close-up photograph of the repaired structure.",
            "5. Submit the image proof through this dashboard to activate AI verification."
        ]
    }
