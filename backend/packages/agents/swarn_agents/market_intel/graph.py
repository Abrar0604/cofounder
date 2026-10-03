from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from .nodes import gather_intel, run_decision

def build_market_intel_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def gather_node(state):
        return await gather_intel(deps, state)
        
    async def decision_node(state):
        return await run_decision(deps, state)
        
    workflow.add_node("gather", gather_node)
    workflow.add_node("decision", decision_node)
    
    workflow.add_edge(START, "gather")
    workflow.add_edge("gather", "decision")
    workflow.add_edge("decision", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="market_intel",
        allowed_tools=frozenset(["search_market_data", "fetch_competitor_metrics"]),
        consumes=frozenset(["user_request", "market_changed"]),
        emits=frozenset(["market_data_gathered", "market_size_evaluated"]),
        build_graph=build_market_intel_graph
    )
