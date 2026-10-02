from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState

async def create_campaign(state: AgentState):
    return {"status": "campaign_created"}

def create_marketing_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("campaign", create_campaign)
    workflow.set_entry_point("campaign")
    workflow.add_edge("campaign", END)
    return workflow.compile()
