import uuid
import datetime
from sqlalchemy.orm import Session
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models import Grievance, AuditLog, Department
from app.services.analytics import recalculate_all_wards
from app.services.notification import notification_service
# We will import the compiled LangGraph workflow later or simulate it in the task directly

@celery_app.task(name="tasks.process_grievance_intake")
def process_grievance_intake(grievance_id_str: str):
    """
    Asynchronously executes intake processing (voice-to-text, OCR, translation).
    """
    db = SessionLocal()
    try:
        g_id = uuid.UUID(grievance_id_str)
        grievance = db.query(Grievance).filter_by(id=g_id).first()
        if not grievance:
            print(f"Grievance {grievance_id_str} not found for intake.")
            return
            
        print(f"[CELERY] Starting intake for grievance: {grievance.title}")
        # Execute LangGraph nodes / intake logic
        # For simplicity, we trigger the next auto-routing stage directly or run the graph.
        db.commit()
        
        # Dispatch next stage: classification and routing
        auto_route_grievance.delay(grievance_id_str)
        
    except Exception as e:
        print(f"Error in process_grievance_intake: {e}")
    finally:
        db.close()

@celery_app.task(name="tasks.auto_route_grievance")
def auto_route_grievance(grievance_id_str: str):
    """
    Asynchronously executes classification, duplicate checks, and queue routing.
    """
    db = SessionLocal()
    try:
        g_id = uuid.UUID(grievance_id_str)
        grievance = db.query(Grievance).filter_by(id=g_id).first()
        if not grievance:
            return
            
        print(f"[CELERY] Running Auto Routing for grievance: {grievance.title}")
        
        # Here we would run the LangGraph compiled state machine.
        # We simulate the transitions directly in the worker task:
        # 1. Check classification confidence (simulate or run agent)
        # 2. Check duplicates (pgvector simulation)
        # 3. Route to queue
        db.commit()
        
    except Exception as e:
        print(f"Error in auto_route_grievance: {e}")
    finally:
        db.close()

@celery_app.task(name="tasks.check_sla_escalations")
def check_sla_escalations():
    """
    SLA Escalation scan: triggered periodically (e.g., hourly) to find open grievances 
    that have exceeded their SLA deadlines and escalate them.
    """
    db = SessionLocal()
    try:
        now = datetime.datetime.utcnow()
        # Find active routed or assigned grievances that have passed SLA
        escalated_grievances = db.query(Grievance).filter(
            Grievance.status.in_(["ROUTED", "ASSIGNED"]),
            Grievance.sla_deadline.isnot(None),
            Grievance.sla_deadline < now
        ).all()
        
        print(f"[CELERY] Checking SLAs. Found {len(escalated_grievances)} grievances to escalate.")
        
        for g in escalated_grievances:
            # Shift priority to EMERGENCY if not already
            old_priority = g.priority
            g.priority = "EMERGENCY"
            
            # Log escalation audit
            audit = AuditLog(
                grievance_id=g.id,
                action="SLA_ESCALATION",
                old_status=g.status,
                new_status=g.status,
                rationale=f"SLA deadline ({g.sla_deadline}) exceeded. Priority escalated from {old_priority} to EMERGENCY."
            )
            db.add(audit)
            
            # Notify Department Head and MP
            dept = db.query(Department).filter_by(id=g.department_id).first()
            dept_name = dept.name if dept else "Unknown Department"
            
            notification_service.send_sms(
                phone="+919999999902", # MP Phone
                message=f"ESCALATION ALERT: Grievance ID {g.id} ({g.title}) in {dept_name} has breached its SLA. Action required."
            )
            
        db.commit()
        print("[CELERY] SLA Escalation check complete.")
    except Exception as e:
        print(f"Error in check_sla_escalations: {e}")
        db.rollback()
    finally:
        db.close()

@celery_app.task(name="tasks.aggregate_constituency_analytics")
def aggregate_constituency_analytics():
    """
    Recalculates constituency health metrics periodically to populate dashboards.
    """
    db = SessionLocal()
    try:
        print("[CELERY] Recalculating Constituency Health Index snapshots...")
        recalculate_all_wards(db)
        print("[CELERY] Analytics snapshot aggregation complete.")
    except Exception as e:
        print(f"Error in aggregate_constituency_analytics: {e}")
    finally:
        db.close()
