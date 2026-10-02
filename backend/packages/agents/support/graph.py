from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState

async def resolve_ticket(state: AgentState):
    return {"status": "ticket_resolved"}

def create_support_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("resolve", resolve_ticket)
    workflow.set_entry_point("resolve")
    workflow.add_edge("resolve", END)
    return workflow.compile()
