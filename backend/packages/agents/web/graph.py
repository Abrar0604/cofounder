from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState

async def web_search(state: AgentState):
    return {"status": "search_completed"}

def create_web_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("search", web_search)
    workflow.set_entry_point("search")
    workflow.add_edge("search", END)
    return workflow.compile()
