from typing import Dict, Any

def set_goal(venture_id: str, constraints: Dict[str, Any]) -> str:
    """
    Pure function to translate constraints into a clear string goal for the orchestrator.
    """
    budget = constraints.get("budget", 0)
    timeline = constraints.get("timeline_weeks", 0)
    
    if budget > 0 and timeline > 0:
        return f"Launch venture {venture_id} within {timeline} weeks under ${budget}."
    elif budget > 0:
        return f"Build venture {venture_id} efficiently under ${budget}."
    elif timeline > 0:
        return f"Build venture {venture_id} within {timeline} weeks."
    else:
        return f"Explore viability for venture {venture_id}."
