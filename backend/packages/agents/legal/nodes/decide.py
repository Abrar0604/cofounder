from typing import Dict, Any
from packages.agents.state import AgentState

async def answer_or_abstain(state: AgentState) -> Dict[str, Any]:
    """Decide whether to answer the legal question or abstain if too risky."""
    context = state.get("context", {})
    docs = context.get("legal_documents", [])
    
    # Mock decision logic
    if not docs:
        return {"status": "abstained", "error": "Insufficient legal context to answer."}
        
    return {"status": "answered", "current_agent": "legal_answered"}
