from packages.agents.swarn_agents.orchestrator.state import OrchestratorState
from packages.decisions.swarn_decisions.definitions.fan_out_event import FanOutEventState

async def handle_event_for_replan(deps, state: OrchestratorState, agent_specs: dict) -> dict:
    events = state.get("events", [])
    if not events:
        return {}
        
    last_event = events[-1]
    event_type = last_event.get("type", "unknown")
    
    # Filter available agents by what they consume
    available_agents = [
        name for name, spec in agent_specs.items()
        if event_type in spec.consumes
    ]
    
    fan_out = FanOutEventState(
        event_type=event_type,
        event_payload=str(last_event.get("payload", {})),
        available_agents=available_agents
    )
    
    decision = await deps.decisions.run('fan_out_event', fan_out)
    
    if not decision:
        return {}
        
    action = getattr(decision, "action", getattr(decision, "choice", "none"))
    # Validate the choice is in the filtered available_agents list
    if action == 'none' or action not in available_agents:
        return {}
        
    # Queue the awakened agent safely without mutating the original state list
    next_agents = list(state.get("next_agents", []))
    if action not in next_agents and action != state.get("active_agent"):
        next_agents.append(action)
        
    return {"next_agents": next_agents}
