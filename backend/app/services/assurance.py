import datetime
from sqlalchemy.orm import Session
from app.models import Grievance, Evidence, AuditLog, User
from app.services.ai import ai_service
from app.services.notification import notification_service
from typing import Dict, Any
from uuid import UUID

def run_resolution_assurance(
    db: Session, 
    grievance_id: UUID, 
    officer_id: UUID, 
    proof_url: str, 
    notes: str = ""
) -> Dict[str, Any]:
    """
    Resolution Assurance Agent.
    Verifies completeness of the officer's work by comparing before-and-after evidence.
    """
    print(f"[ASSURANCE] Starting image-based verification for grievance: {grievance_id}")
    grievance = db.query(Grievance).filter_by(id=grievance_id).first()
    if not grievance:
        return {"success": False, "message": "Grievance not found."}
        
    # Get intake evidence (before image)
    intake_evidence = db.query(Evidence).filter_by(
        grievance_id=grievance_id, 
        type="intake_evidence"
    ).order_by(Evidence.created_at.desc()).first()
    
    intake_url = intake_evidence.media_url if intake_evidence else None
    
    # Trigger AI Image verification
    print("  Comparing before-and-after images via Vision LLM...")
    report = ai_service.verify_images(intake_url, proof_url)
    
    is_ok = report.get("is_verified", False)
    confidence = report.get("match_confidence", 0.0)
    remarks = report.get("remarks", "No vision comparison available.")
    
    # Save the resolution evidence
    evidence = Evidence(
        grievance_id=grievance_id,
        uploader_id=officer_id,
        media_url=proof_url,
        notes=notes,
        type="closure_proof",
        verification_report=report
    )
    db.add(evidence)
    
    if is_ok and confidence >= 0.80:
        print("  AI Validation Successful! Setting status to RESOLVED.")
        old_status = grievance.status
        grievance.status = "RESOLVED"
        
        # Log resolution audit
        audit = AuditLog(
            grievance_id=grievance_id,
            user_id=officer_id,
            action="ResolutionAssuranceAgent",
            old_status=old_status,
            new_status="RESOLVED",
            rationale=f"AI Resolution Verification Passed (Confidence: {confidence:.2f}). Remarks: {remarks}"
        )
        db.add(audit)
        db.commit()
        
        # Send WhatsApp closure notification to Citizen
        citizen = grievance.citizen_id
        # Query citizen phone
        citizen_user = db.query(User).filter_by(id=citizen).first()
        citizen_phone = citizen_user.phone_number if citizen_user else "+919876543210"
        
        # Send WhatsApp template
        notification_service.send_whatsapp_template(
            phone=citizen_phone,
            template_name="grievance_closure_verification",
            parameters={
                "grievance_title": grievance.title,
                "grievance_id": str(grievance.id),
                "resolution_notes": notes
            }
        )
        
        return {
            "success": True,
            "message": "AI Verification passed. Status updated to RESOLVED. Notification dispatched to citizen.",
            "report": report
        }
    else:
        print("  AI Validation Failed! Keeping in ASSIGNED status.")
        # Log failure audit
        audit = AuditLog(
            grievance_id=grievance_id,
            user_id=officer_id,
            action="ResolutionAssuranceAgent",
            old_status=grievance.status,
            new_status=grievance.status,
            rationale=f"AI Resolution Verification Failed (Confidence: {confidence:.2f}). Remarks: {remarks}"
        )
        db.add(audit)
        db.commit()
        
        return {
            "success": False,
            "message": f"AI Verification failed (Confidence: {confidence:.2f}). Remarks: {remarks}",
            "report": report
        }
