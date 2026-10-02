from typing import Any, Dict
from packages.agents.state import AgentState

async def router_node(state: AgentState) -> Dict[str, Any]:
    task = state.get("task", "").lower()
    
    # Simple routing logic
    if "market" in task:
        next_agent = "market_intel"
    elif "validate" in task or "validation" in task:
        next_agent = "validation"
    elif "finance" in task or "financial" in task:
        next_agent = "financial"
    else:
        next_agent = "end"
        
    return {"current_agent": next_agent}
