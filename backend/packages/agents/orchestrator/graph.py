from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState
from packages.agents.orchestrator.nodes.router import router_node

def route_next(state: AgentState) -> str:
    agent = state.get("current_agent")
    if agent in ["market_intel", "validation", "financial"]:
        return agent
    return END

def create_orchestrator_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("router", router_node)
    
    # These would normally be the actual subgraphs/agents
    # Here we mock them for the orchestrator routing
    async def dummy_agent_node(state: AgentState):
        return {"status": "completed"}
        
    workflow.add_node("market_intel", dummy_agent_node)
    workflow.add_node("validation", dummy_agent_node)
    workflow.add_node("financial", dummy_agent_node)
    
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_next,
        {
            "market_intel": "market_intel",
            "validation": "validation",
            "financial": "financial",
            END: END
        }
    )
    
    workflow.add_edge("market_intel", END)
    workflow.add_edge("validation", END)
    workflow.add_edge("financial", END)
    
    return workflow.compile()
