from packages.decisions.ports import Decision

def apply_threshold(decision: Decision, auto_threshold: float = 0.9, confirm_threshold: float = 0.7) -> str:
    """
    Applies business policy thresholds to a model's decision confidence.
    Returns: 'AUTO', 'CONFIRM', or 'ESCALATE'
    """
    if decision.confidence >= auto_threshold:
        return "AUTO"
    elif decision.confidence >= confirm_threshold:
        return "CONFIRM"
    else:
        return "ESCALATE"
