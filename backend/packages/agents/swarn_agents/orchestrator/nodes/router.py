from packages.agents.swarn_agents.orchestrator.state import OrchestratorState
from packages.decisions.swarn_decisions.definitions.route_supervisor import RouteSupervisorState

async def choose_next_agent(deps, state: OrchestratorState, available_agents: list[str]) -> dict:
    
    next_agents = state.get("next_agents", [])
    if next_agents:
        # If there are queued agents, respect the queue
        return {"next_agents": next_agents}
        
    route_state = RouteSupervisorState(
        task=state.get("task", ""),
        active_agent=state.get("active_agent", "none"),
        available_agents=available_agents
    )
    
    decision = await deps.decisions.run('route_supervisor', route_state)
    
    if decision.choice == 'end' or decision.choice not in available_agents:
        return {"next_agents": []}
        
    # Return the next agent to route to
    return {"next_agents": [decision.choice]}
