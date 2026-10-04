from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.base.agent_spec import AgentSpec
from packages.agents.swarn_agents.legal.nodes import run_legal_compliance

def build_legal_graph(deps):
    workflow = StateGraph(AgentState)
    
    async def legal_node(state):
        return await run_legal_compliance(deps, state)
        
    workflow.add_node("legal_compliance", legal_node)
    
    workflow.add_edge(START, "legal_compliance")
    workflow.add_edge("legal_compliance", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)

def get_spec() -> AgentSpec:
    return AgentSpec(
        name="legal",
        allowed_tools=frozenset(["search_compliance_rules"]),
        consumes=frozenset(["user_request", "compliance_checked"]),
        emits=frozenset(["compliance_passed", "compliance_escalation_required"]),
        build_graph=build_legal_graph
    )
