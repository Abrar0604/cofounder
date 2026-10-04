from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.qualify_lead import QualifyLeadState

async def qualify_lead_node(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    task = state.get("request_text") or state.get("task", "")
    
    score = 50
    for e in reversed(events):
        if "lead_score" in e.get("payload", {}):
            score = int(e["payload"]["lead_score"])
            break
            
    d_state = QualifyLeadState(
        task=task,
        lead_score=score
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
