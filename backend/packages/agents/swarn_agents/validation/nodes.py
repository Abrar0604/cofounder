from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.score_viability import ScoreViabilityState
from .tools import check_compliance_rules

async def validate_model(deps, state: AgentState) -> dict:
    industry_hint = state.get("task", "general")
    rules = check_compliance_rules(industry_hint)
    
    events = list(state.get("events", []))
    events.append({"type": "compliance_checked", "payload": rules})
    return {"events": events}

async def score_viability_node(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    
    # Extract market size from earlier events
    market_eval = next((e for e in reversed(events) if e["type"] == "market_size_evaluated"), None)
    market_size = market_eval["payload"].get("size", "missing") if market_eval else "missing"
    
    # Extract compliance check
    compliance_eval = next((e for e in reversed(events) if e["type"] == "compliance_checked"), None)
    compliance = "missing"
    if compliance_eval:
        rules_list = compliance_eval["payload"].get("rules", [])
        compliance = "high" if len(rules_list) > 1 else "low"
        
    d7_state = ScoreViabilityState(
        market_size=market_size,
        compliance_complexity=compliance,
        competitor_density="missing" # competitor evidence is not explicitly gathered yet
    )
    
    decision = await deps.decisions.run('score_viability', d7_state)
    
    events.append({"type": "viability_scored", "payload": {"score": decision.action}})
    return {"events": events}
