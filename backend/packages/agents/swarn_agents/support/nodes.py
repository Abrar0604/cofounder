from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.detect_frustration import DetectFrustrationState

async def detect_frustration_node(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    task = state.get("request_text") or state.get("task", "")
    
    d_state = DetectFrustrationState(
        task=task,
        sentiment="neutral"
    )
    
    decision = await deps.decisions.run('detect_frustration', d_state)
    
    events.append({
        "type": "frustration_detected",
        "payload": {
            "analysis": decision.reasoning,
            "status": decision.action
        }
    })
    
    return {"events": events}
