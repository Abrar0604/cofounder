from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.qualify_lead import QualifyLeadState

async def qualify_lead_node(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    task = state.get("request_text") or state.get("task", "")
    
    d_state = QualifyLeadState(
        task=task,
        lead_score=50
    )
    
    decision = await deps.decisions.run('qualify_lead', d_state)
    
    events.append({
        "type": "lead_qualified",
        "payload": {
            "result": decision.reasoning,
            "status": decision.action
        }
    })
    
    return {"events": events}
