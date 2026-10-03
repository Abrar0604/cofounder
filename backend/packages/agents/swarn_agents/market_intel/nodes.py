from typing import Dict, Any
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.evaluate_market_size import EvaluateMarketSizeState
from .tools import search_market_data

async def gather_intel(deps, state: AgentState) -> dict:
    task = state.get("task", "")
    # Minimal logic: search based on task
    results = await search_market_data(task)
    
    # Store results in events or artifacts
    return {"events": [{"type": "market_data_gathered", "payload": results}]}

async def run_decision(deps, state: AgentState) -> dict:
    # Run D1 decision
    events = state.get("events", [])
    data_summary = str(events[-1].get("payload", "")) if events else "none"
    
    d1_state = EvaluateMarketSizeState(
        market_data_summary=data_summary[:500],
        target_demographic="general"
    )
    
    decision = await deps.decisions.run('evaluate_market_size', d1_state)
    
    return {"events": [{"type": "market_size_evaluated", "payload": {"size": decision.choice}}]}
