def resolve_conflict(agent_a_view: str, agent_b_view: str) -> str:
    """
    Pure function to determine how to resolve conflicting views from two agents.
    Returns the resolution strategy or combined view.
    """
    # Simple deterministic rule for now: combine them
    return f"Conflict detected. Agent A says: {agent_a_view}. Agent B says: {agent_b_view}. Resolution: Require founder input."
