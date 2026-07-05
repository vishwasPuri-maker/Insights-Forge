from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from typing import Optional
from agents.router import MultiAgentRouter

router = APIRouter()
agent_orchestrator = MultiAgentRouter()

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    response_mode: Optional[str] = "MODE_BUSINESS"

# Mock function to simulate token verification and extracting tenant context
async def get_tenant_id(authorization: str = Header(default="Bearer mock-token")):
    return "mock-tenant-uuid"

@router.post("/completions")
async def chat_completion(
    request: ChatRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Standard REST conversational endpoint for Apex AI.
    Routes the natural language query through the Multi-Agent orchestrator.
    """
    result = agent_orchestrator.route_query(request.query, tenant_id, request.response_mode)
    
    return {
        "status": "success",
        "agent": result["role"],
        "analysis_type": result.get("analysis_type", "general"),
        "message": result["response"],
        "confidence": result["confidence"],
        "visualization_payload": None # Could be populated with ECharts data
    }
