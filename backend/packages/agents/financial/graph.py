from typing import Dict, Any
from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState

async def calculate_revenue(state: AgentState) -> Dict[str, Any]:
    return {"status": "revenue_calculated"}

async def calculate_costs(state: AgentState) -> Dict[str, Any]:
    return {"status": "costs_calculated"}

def create_financial_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("revenue", calculate_revenue)
    workflow.add_node("costs", calculate_costs)
    
    workflow.set_entry_point("revenue")
    workflow.add_edge("revenue", "costs")
    workflow.add_edge("costs", END)
    
    return workflow.compile()
