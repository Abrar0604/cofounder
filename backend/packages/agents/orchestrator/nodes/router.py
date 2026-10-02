from typing import Any, Dict
from packages.agents.state import AgentState

async def router_node(state: AgentState) -> Dict[str, Any]:
    task = state.get("task", "").lower()
    
    # Scoring-based routing logic
    scores = {
        "market_intel": task.count("market") + task.count("competitor"),
        "validation": task.count("validate") + task.count("validation") + task.count("fit"),
        "financial": task.count("finance") + task.count("financial") + task.count("cost") + task.count("revenue"),
        "legal": task.count("legal") + task.count("compliance") + task.count("law"),
        "marketing": task.count("marketing") + task.count("campaign"),
        "sales": task.count("sale") + task.count("lead"),
        "support": task.count("support") + task.count("ticket"),
        "web": task.count("web") + task.count("site")
    }
    
    best_match = max(scores.items(), key=lambda x: x[1])
    
    if best_match[1] > 0:
        next_agent = best_match[0]
    else:
        next_agent = "end"
        
    return {"current_agent": next_agent}
