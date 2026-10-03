from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from .nodes import review_financials, assess_burn

def build_financial_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def review_node(state):
        return await review_financials(deps, state)
        
    async def assess_node(state):
        return await assess_burn(deps, state)
        
    workflow.add_node("review", review_node)
    workflow.add_node("assess", assess_node)
    
    workflow.add_edge(START, "review")
    workflow.add_edge("review", "assess")
    workflow.add_edge("assess", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="financial",
        allowed_tools=frozenset(["check_spend", "simulate_revenue_model"]),
        consumes=frozenset(["user_request", "budget_updated"]),
        emits=frozenset(["financials_reviewed", "burn_rate_assessed"]),
        build_graph=build_financial_graph
    )
