from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.orchestrator.state import OrchestratorState
from packages.agents.swarn_agents.orchestrator.nodes.intent import classify_intent
from packages.agents.swarn_agents.orchestrator.nodes.router import choose_next_agent
from packages.agents.swarn_agents.orchestrator.nodes.dispatch import dispatch_agent
from packages.agents.swarn_agents.orchestrator.nodes.summarize import summarize_for_founder
from packages.agents.swarn_agents.orchestrator.nodes.events import handle_event_for_replan
from packages.agents.swarn_agents.base.compact_context import compact_messages

def build_orchestrator_graph(deps, agent_specs: dict):
    workflow = StateGraph(OrchestratorState)
    
    from langchain_core.messages import RemoveMessage
    
    # Define wrappers to inject deps
    async def compact_node(state):
        ctx = state.get("ctx")
        venture_id = state.get("venture_id")
        msgs = state.get("messages", [])
        new_msgs = await compact_messages(deps, None, ctx, venture_id, msgs)
        
        new_msg_ids = {m.id for m in new_msgs if hasattr(m, 'id') and m.id}
        removals = []
        for m in msgs:
            if hasattr(m, 'id') and m.id and m.id not in new_msg_ids:
                removals.append(RemoveMessage(id=m.id))
                
        return {"messages": removals}
        
    async def intent_node(state):
        return await classify_intent(deps, state)
        
    async def router_node(state):
        return await choose_next_agent(deps, state, list(agent_specs.keys()))
        
    async def dispatch_node(state):
        return await dispatch_agent(deps, state)
        
    async def summarize_node(state):
        return await summarize_for_founder(deps, state)
        
    async def event_node(state):
        return await handle_event_for_replan(deps, state, agent_specs)
        
    # Add nodes
    workflow.add_node("compact", compact_node)
    workflow.add_node("intent", intent_node)
    workflow.add_node("router", router_node)
    workflow.add_node("dispatch", dispatch_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("event_replan", event_node)
    
    # Dynamically attach agent subgraphs from registry
    for name, spec in agent_specs.items():
        workflow.add_node(name, spec.build_graph(deps))
        workflow.add_edge(name, "event_replan")
    
    # Edges
    workflow.add_edge(START, "compact")
    workflow.add_edge("compact", "intent")
    
    # Basic logic: Intent -> Router -> Dispatch -> (Agent Subgraphs) -> Event Replan -> Router
    workflow.add_edge("intent", "router")
    workflow.add_edge("router", "dispatch")
    
    def route_dispatch(state):
        active = state.get("active_agent")
        if not active or active not in agent_specs:
            return "summarize"
        return active
        
    # We must map every possible agent string explicitly for LangGraph validation
    dispatch_mapping = {"summarize": "summarize"}
    for name in agent_specs.keys():
        dispatch_mapping[name] = name
        
    workflow.add_conditional_edges("dispatch", route_dispatch, dispatch_mapping)
    
    def route_event_replan(state):
        if state.get("next_agents"):
            return "router"
        return "summarize"
        
    workflow.add_conditional_edges("event_replan", route_event_replan, {"router": "router", "summarize": "summarize"})
    workflow.add_edge("summarize", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)
