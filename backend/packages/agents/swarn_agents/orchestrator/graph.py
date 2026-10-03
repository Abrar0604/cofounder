from langgraph.graph import StateGraph, START, END
from packages.agents.swarn_agents.orchestrator.state import OrchestratorState
from packages.agents.swarn_agents.orchestrator.nodes.intent import classify_intent
from packages.agents.swarn_agents.orchestrator.nodes.router import choose_next_agent
from packages.agents.swarn_agents.orchestrator.nodes.dispatch import dispatch_agent
from packages.agents.swarn_agents.orchestrator.nodes.summarize import summarize_for_founder
from packages.agents.swarn_agents.orchestrator.nodes.events import handle_event_for_replan
from packages.agents.swarn_agents.base.compact_context import compact_messages

def build_orchestrator_graph(deps):
    workflow = StateGraph(OrchestratorState)
    
    # Define wrappers to inject deps
    async def compact_node(state):
        ctx = state.get("ctx")
        venture_id = state.get("venture_id")
        msgs = state.get("messages", [])
        new_msgs = await compact_messages(deps, None, ctx, venture_id, msgs)
        return {"messages": new_msgs}
        
    async def intent_node(state):
        return await classify_intent(deps, state)
        
    async def router_node(state):
        return await choose_next_agent(deps, state)
        
    async def dispatch_node(state):
        return await dispatch_agent(deps, state)
        
    async def summarize_node(state):
        return await summarize_for_founder(deps, state)
        
    async def event_node(state):
        return await handle_event_for_replan(deps, state)
        
    # Add nodes
    workflow.add_node("compact", compact_node)
    workflow.add_node("intent", intent_node)
    workflow.add_node("router", router_node)
    workflow.add_node("dispatch", dispatch_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("event_replan", event_node)
    
    # Edges
    workflow.add_edge(START, "compact")
    workflow.add_edge("compact", "intent")
    
    # Basic logic: Intent -> Router -> Dispatch -> (Agent Subgraphs) -> Event Replan -> Router
    workflow.add_edge("intent", "router")
    workflow.add_edge("router", "dispatch")
    
    def route_dispatch(state):
        active = state.get("active_agent")
        if not active:
            return "summarize"
        # In a real setup, we would route to the active_agent's node
        return "summarize"
        
    workflow.add_conditional_edges("dispatch", route_dispatch, {"summarize": "summarize"})
    workflow.add_edge("summarize", END)
    
    return workflow.compile(checkpointer=deps.checkpointer if hasattr(deps, 'checkpointer') else None)
