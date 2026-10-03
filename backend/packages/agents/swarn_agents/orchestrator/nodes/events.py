from packages.agents.swarn_agents.orchestrator.state import OrchestratorState
from packages.decisions.swarn_decisions.definitions.fan_out_event import FanOutEventState
from packages.agents.swarn_agents.registry import AGENT_SPECS

async def handle_event_for_replan(deps, state: OrchestratorState) -> dict:
    events = state.get("events", [])
    if not events:
        return {}
        
    last_event = events[-1]
    
    fan_out = FanOutEventState(
        event_type=last_event.get("type", "unknown"),
        event_payload=str(last_event.get("payload", {})),
        available_agents=list(AGENT_SPECS.keys())
    )
    
    decision = await deps.decisions.run('fan_out_event', fan_out)
    
    if decision.choice == 'none' or decision.choice not in AGENT_SPECS:
        return {}
        
    # Queue the awakened agent
    next_agents = state.get("next_agents", [])
    if decision.choice not in next_agents and decision.choice != state.get("active_agent"):
        next_agents.append(decision.choice)
        
    return {"next_agents": next_agents}
