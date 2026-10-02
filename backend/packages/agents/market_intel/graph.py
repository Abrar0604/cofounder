from typing import Dict, Any
from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState

async def analyze_market(state: AgentState) -> Dict[str, Any]:
    return {"status": "market_analyzed"}

async def gather_competitors(state: AgentState) -> Dict[str, Any]:
    return {"status": "competitors_gathered"}

def create_market_intel_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyze", analyze_market)
    workflow.add_node("competitors", gather_competitors)
    
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "competitors")
    workflow.add_edge("competitors", END)
    
    return workflow.compile()
