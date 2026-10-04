from typing import TypedDict, Optional, List
from packages.agents.swarn_agents.base.agent_state import AgentState

class OrchestratorState(AgentState):
    active_agent: Optional[str]
    agent_hops: int
    next_agents: List[str]
    summary: Optional[str]
    needs_clarification: Optional[bool]
    survey_results: Optional[dict]
