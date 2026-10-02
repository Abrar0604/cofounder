from typing import Dict, Any
from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState

async def validate_idea(state: AgentState) -> Dict[str, Any]:
    return {"status": "idea_validated"}

def create_validation_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("validate", validate_idea)
    workflow.set_entry_point("validate")
    workflow.add_edge("validate", END)
    
    return workflow.compile()
