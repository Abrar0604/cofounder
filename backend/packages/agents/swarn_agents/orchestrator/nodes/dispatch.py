from packages.agents.swarn_agents.orchestrator.state import OrchestratorState

async def dispatch_agent(deps, state: OrchestratorState) -> dict:
    next_agents = state.get("next_agents", [])
    
    if not next_agents:
        return {"active_agent": None}
        
    # Dispatch simply marks the next agent as active.
    # The LangGraph router will read `active_agent` to branch.
    active = next_agents[0]
    
    hops = state.get("agent_hops", 0) + 1
    
    return {
        "active_agent": active,
        "agent_hops": hops,
        "next_agents": next_agents[1:]
    }
