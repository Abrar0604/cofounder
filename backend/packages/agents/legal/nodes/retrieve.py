from typing import Dict, Any
from packages.agents.state import AgentState

async def retrieve_legal_context(state: AgentState) -> Dict[str, Any]:
    """Retrieve relevant legal documents based on the task."""
    task = state.get("task", "")
    
    # Mock retrieval logic
    retrieved_docs = [
        {"id": "doc1", "text": "Startups must register with the state."},
        {"id": "doc2", "text": "Securities regulations apply to equity issuance."}
    ]
    
    context = dict(state.get("context", {}))
    context["legal_documents"] = retrieved_docs
    
    return {"status": "context_retrieved", "context": context}
