from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState
from packages.agents.orchestrator.nodes.router import router_node
from packages.agents.market_intel.graph import create_market_intel_graph
from packages.agents.validation.graph import create_validation_graph
from packages.agents.financial.graph import create_financial_graph
from packages.agents.legal.graph import create_legal_graph
from packages.agents.marketing.graph import create_marketing_graph
from packages.agents.sales.graph import create_sales_graph
from packages.agents.support.graph import create_support_graph
from packages.agents.web.graph import create_web_graph

def route_next(state: AgentState) -> str:
    agent = state.get("current_agent")
    agents = ["market_intel", "validation", "financial", "legal", "marketing", "sales", "support", "web"]
    if agent in agents:
        return agent
    return END

def create_orchestrator_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("router", router_node)
    
    workflow.add_node("market_intel", create_market_intel_graph())
    workflow.add_node("validation", create_validation_graph())
    workflow.add_node("financial", create_financial_graph())
    workflow.add_node("legal", create_legal_graph())
    workflow.add_node("marketing", create_marketing_graph())
    workflow.add_node("sales", create_sales_graph())
    workflow.add_node("support", create_support_graph())
    workflow.add_node("web", create_web_graph())
    
    workflow.set_entry_point("router")
    
    agents = ["market_intel", "validation", "financial", "legal", "marketing", "sales", "support", "web"]
    
    condition_map = {agent: agent for agent in agents}
    condition_map[END] = END
    
    workflow.add_conditional_edges(
        "router",
        route_next,
        condition_map
    )
    
    for agent in agents:
        workflow.add_edge(agent, END)
    
    return workflow.compile()
