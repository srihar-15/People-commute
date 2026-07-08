from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.grievance import Grievance
from app.models.health import ConstituencyHealthIndex
from app.models.department import Department
import datetime
from typing import Dict, Any, List

def calculate_ward_health(db: Session, ward_id: str) -> ConstituencyHealthIndex:
    """
    Computes category health scores out of 100 for a specific ward.
    Deducts points for open/escalated grievances:
      - LOW: -1 point
      - MEDIUM: -3 points
      - HIGH: -5 points
      - EMERGENCY: -10 points
    Double deductions apply if the SLA deadline has passed (escalated).
    """
    # Fetch all open grievances for the ward
    open_grievances = db.query(Grievance).filter(
        Grievance.status != "CLOSED",
        Grievance.latitude.isnot(None), # Ensure it is geotagged
        # In a real environment, match geographic boundaries.
        # For our MVP ward mock, we match string values mapped in title/description or a dummy assignment:
    ).all()
    
    # Simple simulation: group open grievances by ward. 
    # Since grievances in seed data have a specific ward string in their details,
    # let's filter by ward match in description/title for our demo wards:
    ward_grievances = []
    for g in open_grievances:
        # Match ward name in grievance description or title
        if ward_id.split(" ")[0].lower() in g.description.lower() or ward_id.split(" ")[0].lower() in g.title.lower():
            ward_grievances.append(g)
            
    # Base scores
    scores = {
        "WATER": 100.0,
        "ROADS": 100.0,
        "SANITATION": 100.0,
        "ELECTRICITY": 100.0,
        "EDUCATION": 100.0,      # Default high since no active mock complaints exist
        "HEALTHCARE": 100.0,     # Default high
        "SAFETY": 100.0
    }
    
    now = datetime.datetime.utcnow()
    
    for g in ward_grievances:
        # Deduct weight
        weight = 3.0 # MEDIUM
        if g.priority == "LOW":
            weight = 1.0
        elif g.priority == "HIGH":
            weight = 5.0
        elif g.priority == "EMERGENCY":
            weight = 10.0
            
        # Double weight if SLA deadline passed
        if g.sla_deadline and g.sla_deadline < now.replace(tzinfo=datetime.timezone.utc if g.sla_deadline.tzinfo else None):
            weight *= 2.0
            
        # Map department to category
        dept_code = "SAFETY" # Default
        if g.department_id:
            dept = db.query(Department).filter_by(id=g.department_id).first()
            if dept:
                dept_code = dept.code
                
        if dept_code in scores:
            scores[dept_code] -= weight
            # Bound score to minimum 0.0
            if scores[dept_code] < 0.0:
                scores[dept_code] = 0.0
                
    # overall score
    overall = sum(scores.values()) / len(scores)
    
    snapshot = ConstituencyHealthIndex(
        ward_id=ward_id,
        water_score=round(scores["WATER"], 1),
        roads_score=round(scores["ROADS"], 1),
        electricity_score=round(scores["ELECTRICITY"], 1),
        education_score=round(scores["EDUCATION"], 1),
        healthcare_score=round(scores["HEALTHCARE"], 1),
        sanitation_score=round(scores["SANITATION"], 1),
        safety_score=round(scores["SAFETY"], 1),
        overall_health_index=round(overall, 1),
        computed_at=datetime.datetime.utcnow()
    )
    
    db.add(snapshot)
    db.commit()
    return snapshot

def recalculate_all_wards(db: Session) -> List[ConstituencyHealthIndex]:
    """
    Recalculates scores for all representative wards in Vijayawada.
    """
    wards = ["Ward 1 (Vasant Nagar)", "Ward 2 (Ganesh Nagar)", "Ward 3 (Subhash Nagar)", "Ward 4 (Bhimrao Colony)", "Ward 5 (Shastri Nagar)"]
    snapshots = []
    for w in wards:
        snapshots.append(calculate_ward_health(db, w))
    return snapshots

def get_constituency_kpis(db: Session) -> Dict[str, Any]:
    """
    Provides aggregated metrics for the MP Dashboard.
    """
    total = db.query(func.count(Grievance.id)).scalar()
    open_count = db.query(func.count(Grievance.id)).filter(Grievance.status != "CLOSED").scalar()
    resolved_count = db.query(func.count(Grievance.id)).filter(Grievance.status == "RESOLVED").scalar()
    closed_count = db.query(func.count(Grievance.id)).filter(Grievance.status == "CLOSED").scalar()
    
    # Calculate average resolution time (in hours) for closed complaints
    closed_grievances = db.query(Grievance).filter(
        Grievance.status == "CLOSED",
        Grievance.resolved_at.isnot(None)
    ).all()
    
    total_hours = 0.0
    for g in closed_grievances:
        duration = g.resolved_at - g.created_at
        total_hours += duration.total_seconds() / 3600.0
        
    avg_res_time = round(total_hours / len(closed_grievances), 1) if closed_grievances else 0.0
    
    # Get latest health indexes
    wards = ["Ward 1 (Vasant Nagar)", "Ward 2 (Ganesh Nagar)", "Ward 3 (Subhash Nagar)", "Ward 4 (Bhimrao Colony)", "Ward 5 (Shastri Nagar)"]
    latest_scores = {}
    for w in wards:
        latest = db.query(ConstituencyHealthIndex).filter_by(ward_id=w).order_by(ConstituencyHealthIndex.computed_at.desc()).first()
        if latest:
            latest_scores[w] = latest.overall_health_index
            
    constituency_health = round(sum(latest_scores.values()) / len(latest_scores), 1) if latest_scores else 100.0
    
    return {
        "total_grievances": total,
        "open_grievances": open_count,
        "resolved_grievances": resolved_count,
        "closed_grievances": closed_count,
        "average_resolution_time_hrs": avg_res_time,
        "constituency_health_index": constituency_health,
        "ward_health_breakdown": latest_scores
    }
