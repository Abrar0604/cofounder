from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from .nodes import validate_model, score_viability_node

def build_validation_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def val_node(state):
        return await validate_model(deps, state)
        
    async def score_node(state):
        return await score_viability_node(deps, state)
        
    workflow.add_node("validate", val_node)
    workflow.add_node("score", score_node)
    
    workflow.add_edge(START, "validate")
    workflow.add_edge("validate", "score")
    workflow.add_edge("score", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="validation",
        allowed_tools=frozenset(["check_compliance_rules"]),
        consumes=frozenset(["market_size_evaluated"]),
        emits=frozenset(["compliance_checked", "viability_scored"]),
        build_graph=build_validation_graph
    )
