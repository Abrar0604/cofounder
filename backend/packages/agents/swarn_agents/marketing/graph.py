from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from .nodes import draft_calendar

def build_marketing_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def draft_calendar_node(state):
        return await draft_calendar(deps, state)
        
    workflow.add_node("draft_calendar", draft_calendar_node)
    
    workflow.add_edge(START, "draft_calendar")
    workflow.add_edge("draft_calendar", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="marketing",
        allowed_tools=frozenset([]),
        consumes=frozenset(["user_request"]),
        emits=frozenset(["content_calendar_drafted"]),
        build_graph=build_marketing_graph
    )
