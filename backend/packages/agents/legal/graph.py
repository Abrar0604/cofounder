from typing import Dict, Any
from langgraph.graph import StateGraph, END
from packages.agents.state import AgentState
from packages.agents.legal.nodes.retrieve import retrieve_legal_context
from packages.agents.legal.nodes.decide import answer_or_abstain

def create_legal_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("retrieve", retrieve_legal_context)
    workflow.add_node("decide", answer_or_abstain)
    
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "decide")
    workflow.add_edge("decide", END)
    
    return workflow.compile()
