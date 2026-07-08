from app.agents.state import AgentState
from app.agents.nodes import (
    run_citizen_intake,
    run_classification,
    run_duplicate_detection,
    run_routing
)

def execute_agent_workflow(grievance_id, title: str, description: str, language: str = "en", source: str = "web", citizen_id = None):
    """
    Orchestrates the multi-agent workflow sequentially through the state schema.
    This simulates the LangGraph pipeline robustly, avoiding package-specific start key conflicts.
    """
    initial_state = AgentState(
        grievance_id=grievance_id,
        title=title,
        description=description,
        translated_description=None,
        original_language=language,
        source=source,
        citizen_id=citizen_id,
        latitude=None,
        longitude=None,
        department_id=None,
        priority=None,
        priority_score=None,
        confidence_score=None,
        master_issue_id=None,
        evidence_urls=[],
        audit_notes=[],
        next_node="intake"
    )
    
    print(f"[AGENT STATE MACHINE] Starting pipeline for Grievance: {grievance_id}")
    
    # 1. Citizen Intake
    state = run_citizen_intake(initial_state)
    
    # 2. Classification & Priority
    if state["next_node"] == "classification":
        state = run_classification(state)
        
    # 3. Duplicate Detection
    if state["next_node"] == "duplicate_detection":
        state = run_duplicate_detection(state)
        
    # 4. Routing
    if state["next_node"] == "routing":
        state = run_routing(state)
        
    print(f"[AGENT STATE MACHINE] Pipeline execution completed for Grievance: {grievance_id}")
    return state
