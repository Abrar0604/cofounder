from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.assess_burn_rate import AssessBurnRateState
from .tools import check_spend

async def review_financials(deps, state: AgentState) -> dict:
    venture_id = state.get("venture_id", "default")
    spend_data = await check_spend(venture_id)
    
    events = list(state.get("events", []))
    events.append({"type": "financials_reviewed", "payload": spend_data})
    
    return {"events": events}

async def assess_burn(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    review_event = next((e for e in reversed(events) if e["type"] == "financials_reviewed"), None)
    
    if not review_event:
        # Fallback if somehow node was skipped
        events.append({"type": "burn_rate_assessed", "payload": {"status": "unknown"}})
        return {"events": events}
        
    payload = review_event["payload"]
    d9_state = AssessBurnRateState(
        total_spent=payload.get("total_spent", 0.0),
        budget=payload.get("budget", 0.0),
        burn_rate_per_week=payload.get("burn_rate_per_week", 0.0)
    )
    
    decision = await deps.decisions.run('assess_burn_rate', d9_state)
    
    events.append({"type": "burn_rate_assessed", "payload": {"status": decision.choice}})
    return {"events": events}
