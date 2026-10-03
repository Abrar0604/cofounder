from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph.message import add_messages

# Mock RequestContext for now
class RequestContext:
    def __init__(self, tenant_id: str, user_id: str, role: str):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.role = role

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    tenant_id: str
    venture_id: str
    user_id: str
    role: str
    run_id: str
    agent: str
    task: str
    artifacts: list[str]
    events: list[dict]
    needs_human: bool
    error: Optional[str]

def context_from_state(state: AgentState) -> RequestContext:
    return RequestContext(
        tenant_id=state["tenant_id"],
        user_id=state["user_id"],
        role=state["role"]
    )
