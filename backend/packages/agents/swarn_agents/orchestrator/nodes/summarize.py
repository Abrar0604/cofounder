from packages.agents.swarn_agents.orchestrator.state import OrchestratorState

async def summarize_for_founder(deps, state: OrchestratorState) -> dict:
    # A lightweight summarization step used when returning control to the founder
    model = deps.models.get_model('cheap')
    
    msgs = state.get("messages", [])
    if not msgs:
        return {"summary": "No messages to summarize."}
        
    prompt = "Summarize the current state of the venture's tasks and pending approvals for the founder."
    
    # Normally we would format the history into a neat prompt
    # For now, just a direct completion
    res = await model.ainvoke([{"role": "user", "content": prompt}])
    
    return {"summary": res.content}
