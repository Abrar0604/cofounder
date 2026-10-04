from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.define_landing_page import DefineLandingPageState

async def define_specs(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    
    task = state.get("request_text") or state.get("task", "")
    
    audience = "General"
    for e in reversed(events):
        if "target_audience" in e.get("payload", {}):
            audience = e["payload"]["target_audience"]
            break
            
    d_state = DefineLandingPageState(
        task=task,
        target_audience=audience
    )
    
    decision = await deps.decisions.run('define_landing_page', d_state)
    
    events.append({
        "type": "landing_page_specs_defined",
        "payload": {
            "specs": decision.reasoning,
            "status": decision.action
        }
    })
    
    return {"events": events}
