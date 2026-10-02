from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState

async def lead_generation(state: AgentState):
    return {"status": "leads_generated"}

def create_sales_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("lead_gen", lead_generation)
    workflow.set_entry_point("lead_gen")
    workflow.add_edge("lead_gen", END)
    return workflow.compile()
