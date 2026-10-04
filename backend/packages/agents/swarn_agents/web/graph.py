from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from .nodes import define_specs

def build_web_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def define_specs_node(state):
        return await define_specs(deps, state)
        
    workflow.add_node("define_specs", define_specs_node)
    
    workflow.add_edge(START, "define_specs")
    workflow.add_edge("define_specs", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="web",
        allowed_tools=frozenset([]),
        consumes=frozenset(["user_request"]),
        emits=frozenset(["landing_page_specs_defined"]),
        build_graph=build_web_graph
    )
