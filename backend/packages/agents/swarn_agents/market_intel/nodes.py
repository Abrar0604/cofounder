from typing import Dict, Any
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.evaluate_market_size import EvaluateMarketSizeState
from .tools import search_market_data

async def gather_intel(deps, state: AgentState) -> dict:
    task = state.get("task", "")
    # Minimal logic: search based on task
    results = await search_market_data(task)
    
    events = list(state.get("events", []))
    events.append({"type": "market_data_gathered", "payload": results})
    return {"events": events}

async def run_decision(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    data_gathered = next((e for e in reversed(events) if e["type"] == "market_data_gathered"), None)
    
    if data_gathered and "error" in data_gathered["payload"]:
        # Prevent producing market_size_evaluated without market evidence
        return {"events": events}
        
    data_summary = str(data_gathered.get("payload", "")) if data_gathered else "none"
    
    d1_state = EvaluateMarketSizeState(
        market_data_summary=data_summary[:500],
        target_demographic="general"
    )
    
    decision = await deps.decisions.run('evaluate_market_size', d1_state)
    
    events.append({"type": "market_size_evaluated", "payload": {"size": decision.action}})
    return {"events": events}
