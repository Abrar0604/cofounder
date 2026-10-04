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
    
    # Validate the choice is in the filtered available_agents list
    if not decision or decision.action == 'none' or decision.action not in available_agents:
        return {}
        
    # Queue the awakened agent
    next_agents = state.get("next_agents", [])
    if decision.action not in next_agents and decision.action != state.get("active_agent"):
        next_agents.append(decision.action)
        
    return {"next_agents": next_agents}
