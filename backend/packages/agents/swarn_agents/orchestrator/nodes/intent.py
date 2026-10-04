from packages.agents.swarn_agents.orchestrator.state import OrchestratorState
from packages.decisions.swarn_decisions.definitions.founder_intent import FounderIntentState

async def classify_intent(deps, state: OrchestratorState) -> dict:
    if not state.get("messages"):
        return {"task": "unknown"}
        
    last_msg = state["messages"][-1]
    if getattr(last_msg, "type", "") != "human":
        # Usually intent classification happens on human inputs
        return {}
        
    content = str(getattr(last_msg, "content", ""))
    
    intent_state = FounderIntentState(
        message=content,
        context=state.get("summary", "")
    )
    
    decision = await deps.decisions.run('founder_intent', intent_state)
    
    if not decision:
        return {"task": "unknown", "request_text": content}
    
    return {"task": getattr(decision, "action", getattr(decision, "choice", "unknown")), "request_text": content}
