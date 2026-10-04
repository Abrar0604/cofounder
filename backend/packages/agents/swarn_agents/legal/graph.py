from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from .nodes.retrieve import retrieve_statutes
from .nodes.decide import answer_or_abstain

def build_legal_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def retrieve_node(state):
        return await retrieve_statutes(deps, state)
        
    async def decide_node(state):
        return await answer_or_abstain(deps, state)
        
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("decide", decide_node)
    
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "decide")
    workflow.add_edge("decide", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="legal",
        allowed_tools=frozenset(["search_legal_database"]),
        consumes=frozenset(["user_request", "compliance_checked"]),
        emits=frozenset(["legal_statutes_retrieved", "legal_advice_provided", "legal_advice_abstained"]),
        build_graph=build_legal_graph
    )
