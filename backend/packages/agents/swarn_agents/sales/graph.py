from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from .nodes import qualify_lead_node

def build_sales_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def qualify_node(state):
        return await qualify_lead_node(deps, state)
        
    workflow.add_node("qualify_lead", qualify_node)
    
    workflow.add_edge(START, "qualify_lead")
    workflow.add_edge("qualify_lead", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="sales",
        allowed_tools=frozenset([]),
        consumes=frozenset(["user_request", "meta_event"]),
        emits=frozenset(["lead_qualified"]),
        build_graph=build_sales_graph
    )
