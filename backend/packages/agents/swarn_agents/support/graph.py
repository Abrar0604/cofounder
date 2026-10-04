from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from .nodes import detect_frustration_node

def build_support_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def frustration_node(state):
        return await detect_frustration_node(deps, state)
        
    workflow.add_node("detect_frustration", frustration_node)
    
    workflow.add_edge(START, "detect_frustration")
    workflow.add_edge("detect_frustration", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="support",
        allowed_tools=frozenset([]),
        consumes=frozenset(["user_request", "meta_event"]),
        emits=frozenset(["frustration_detected"]),
        build_graph=build_support_graph
    )
