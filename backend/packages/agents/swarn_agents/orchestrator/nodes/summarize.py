from packages.agents.swarn_agents.orchestrator.state import OrchestratorState

async def summarize_for_founder(deps, state: OrchestratorState) -> dict:
    # A lightweight summarization step used when returning control to the founder
    model = deps.models.get_model('cheap')
    
    msgs = state.get("messages", [])
    if not msgs:
        return {"summary": "No messages to summarize."}
        
    prompt = "Summarize the current state of the venture's tasks and pending approvals for the founder."
    
    # We pass the system prompt first, then append the recent context (e.g. up to 10 messages)
    context = msgs[-10:]
    payload = [{"role": "system", "content": prompt}]
    
    for m in context:
        t = getattr(m, "type", "other")
        c = getattr(m, "content", "")
        payload.append({"role": "user" if t == "human" else "assistant", "content": str(c)})
        
    res = await model.ainvoke(payload)
    
    return {"summary": res.content}
