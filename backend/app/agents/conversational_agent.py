import json
from typing import TypedDict, List, Dict, Optional, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import google.generativeai as genai
from app.services.ai.shared_ai import ai_service

class CitizenChatState(TypedDict):
    user_id: str
    messages: List[Dict[str, str]]
    category: Optional[str]
    location: Optional[str]
    description: Optional[str]
    duration: Optional[str]
    accidents_caused: Optional[str]
    image_url: Optional[str]
    is_complete: bool
    followup_question: str
    grievance_id: Optional[str]

# Node 1: Analyze user input and extract variables
def determine_completeness(state: CitizenChatState) -> CitizenChatState:
    messages = state["messages"]
    
    # Run Gemini Flash model for extraction
    if ai_service.client_enabled:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Format chat history for prompt
            history_str = ""
            for msg in messages:
                history_str += f"{msg['role'].upper()}: {msg['content']}\n"
                
            prompt = (
                "You are an intake bot for a government grievance portal. "
                "Review the conversation history and extract the following variables in JSON format. "
                "Only extract information that is explicitly stated or strongly implied by the citizen. "
                "Fields: \n"
                "- category: one of ['WATER', 'ROADS', 'SANITATION', 'ELECTRICITY', null]\n"
                "- location: exact street, landmark, ward or address, or null\n"
                "- description: short summary of the issue, or null\n"
                "- duration: how long it has been happening, or null\n"
                "- accidents_caused: any accidents or immediate hazards mentioned, or null\n"
                "- is_complete: boolean (true if we have at least category, a description, and a specific location/landmark so that a repair crew can find it. Otherwise false)\n\n"
                "Conversation history:\n"
                f"{history_str}\n\n"
                "Return only the JSON object."
            )
            
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text.strip())
            
            # Merge extracted state
            state["category"] = data.get("category") or state.get("category")
            state["location"] = data.get("location") or state.get("location")
            state["description"] = data.get("description") or state.get("description")
            state["duration"] = data.get("duration") or state.get("duration")
            state["accidents_caused"] = data.get("accidents_caused") or state.get("accidents_caused")
            state["is_complete"] = data.get("is_complete", False)
            
        except Exception as e:
            print(f"Error in determine_completeness node: {e}")
            # Fallback extraction logic
            state["is_complete"] = False
    else:
        # Static mock logic if no API key
        last_msg = messages[-1]["content"].lower()
        if "leak" in last_msg or "water" in last_msg:
            state["category"] = "WATER"
            state["description"] = messages[-1]["content"]
        
        # Simple heuristic completeness check
        if state.get("location") and state.get("description"):
            state["is_complete"] = True
        else:
            state["is_complete"] = False
            
    return state

# Node 2: Generate follow-up questions
def ask_followup(state: CitizenChatState) -> CitizenChatState:
    if state["is_complete"]:
        return state
        
    if ai_service.client_enabled:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            history_str = ""
            for msg in state["messages"]:
                history_str += f"{msg['role'].upper()}: {msg['content']}\n"
                
            prompt = (
                "You are an official Govt of Andhra Pradesh grievance bot. "
                "Based on the conversation history below, draft a single, polite, professional follow-up question "
                "to collect the missing details (e.g., location/landmark, since when, severity, or photo). "
                "Do not repeat questions if they were already answered. Be very concise and speak directly as the bot. "
                "If the citizen has not uploaded a photo, politely remind them they can upload a photo of the defect.\n\n"
                f"Conversation history:\n{history_str}\n"
            )
            response = model.generate_content(prompt)
            state["followup_question"] = response.text.strip()
        except Exception as e:
            print(f"Error in ask_followup node: {e}")
            state["followup_question"] = "Could you please tell me the exact location or landmark near the issue?"
    else:
        # Fallback question heuristics
        if not state.get("location"):
            state["followup_question"] = "Could you please specify the exact location or landmark?"
        elif not state.get("duration"):
            state["followup_question"] = "Since when has this issue been happening?"
        else:
            state["followup_question"] = "Could you please upload a photo of the issue so we can register it accurately?"
            
    return state

# Router logic
def route_next(state: CitizenChatState):
    if state["is_complete"]:
        return "complete"
    else:
        return "ask"

# Initialize graph
workflow = StateGraph(CitizenChatState)

# Add nodes
workflow.add_node("determine_completeness", determine_completeness)
workflow.add_node("ask_followup", ask_followup)

# Set entry point
workflow.set_entry_point("determine_completeness")

# Add conditional routing
workflow.add_conditional_edges(
    "determine_completeness",
    route_next,
    {
        "complete": END,
        "ask": "ask_followup"
    }
)

workflow.add_edge("ask_followup", END)

# Persistent checkpointer for conversation memory
memory = MemorySaver()
citizen_chat_graph = workflow.compile(checkpointer=memory)
