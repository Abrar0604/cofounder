from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.draft_content_calendar import DraftContentCalendarState

async def draft_calendar(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    
    task = state.get("request_text") or state.get("task", "")
    
    timeline = "1 month"
    for e in reversed(events):
        if "timeline" in e.get("payload", {}):
            timeline = e["payload"]["timeline"]
            break
            
    d_state = DraftContentCalendarState(
        task=task,
        timeline=timeline
    )
    
    decision = await deps.decisions.run('draft_content_calendar', d_state)
    
    events.append({
        "type": "content_calendar_drafted",
        "payload": {
            "calendar": decision.reasoning,
            "status": decision.action
        }
    })
    
    return {"events": events}
