class SkipLlm(Exception):
    """Raised when the LLM is not needed for a step, allowing the agent to use a pure fallback."""
    pass
