from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.score_viability import ScoreViabilityState
from .tools import check_compliance_rules

async def validate_model(deps, state: AgentState) -> dict:
    rules = check_compliance_rules("general")
    return {"events": [{"type": "compliance_checked", "payload": rules}]}

async def score_viability_node(deps, state: AgentState) -> dict:
    d7_state = ScoreViabilityState(
        market_size="unknown",
        compliance_complexity="medium",
        competitor_density="high"
    )
    
    decision = await deps.decisions.run('score_viability', d7_state)
    return {"events": [{"type": "viability_scored", "payload": {"score": decision.choice}}]}
