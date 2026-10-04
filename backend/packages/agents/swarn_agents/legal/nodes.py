from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.agents.swarn_agents.models.model_router import ModelRouter
from packages.agents.swarn_agents.legal.tools.retrieve import search_compliance_rules
import json

SYSTEM_PROMPT = """You are the Swarn Legal Compliance Agent.
Your job is to analyze the Venture constraints, search for legal rules using your tool, and determine if the venture passes compliance or needs escalation.

You must reply with a JSON object in the following format (and nothing else):
{
    "decision": "compliance_passed" | "compliance_escalation_required",
    "reasoning": "Detailed explanation of why it passed or failed.",
    "escalation_details": "If failed, what needs to be reviewed by a human." // optional
}
"""

async def run_legal_compliance(deps, state: AgentState) -> Dict[str, Any]:
    # Extract constraints from state
    # We look at task, request_text, and prior events
    task = state.get("task", "")
    request = state.get("request_text", "")
    events = state.get("events", [])
    
    # Try to find venture constraints in events or use task/request
    constraints = f"Task: {task}\nRequest: {request}"
    
    # Get LLM and bind tool
    model = ModelRouter(deps.settings).get_model("cheap")
    model_with_tools = model.bind_tools([search_compliance_rules])
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Please analyze these venture constraints and search for relevant rules:\n{constraints}")
    ]
    
    # We will do a simple tool-calling loop (max 3 iterations)
    for _ in range(3):
        response = await model_with_tools.ainvoke(messages)
        messages.append(response)
        
        if not response.tool_calls:
            break
            
        for tool_call in response.tool_calls:
            if tool_call["name"] == "search_compliance_rules":
                query = tool_call["args"]["query"]
                tool_result = await search_compliance_rules.ainvoke({"query": query})
                from langchain_core.messages import ToolMessage
                messages.append(ToolMessage(
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    content=tool_result
                ))
    
    # Ensure the last message is an AIMessage with the final decision
    if not hasattr(messages[-1], "content") or getattr(messages[-1], "type", "") != "ai" or getattr(messages[-1], "tool_calls", None):
        # It maxed out iterations without a final decision
        messages.append(HumanMessage(content="Please provide your final decision in the requested JSON format based on the information you have so far."))
        final_response = await model.ainvoke(messages)
    else:
        final_response = messages[-1]

    final_text = final_response.content if hasattr(final_response, 'content') else ""
    
    # Let's be robust: if it didn't output JSON, we force it
    try:
        cleaned = final_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        result = json.loads(cleaned.strip())
    except Exception:
        # Force JSON response
        messages.append(HumanMessage(content="Please provide your final decision in the requested JSON format only."))
        final_response = await model.ainvoke(messages)
        cleaned = final_response.content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        try:
            result = json.loads(cleaned.strip())
        except Exception:
            # Fallback if it completely fails
            result = {
                "decision": "compliance_escalation_required",
                "reasoning": "Failed to parse LLM output.",
                "escalation_details": final_response.content
            }
            
    # Process result
    decision = result.get("decision", "compliance_escalation_required")
    events = list(state.get("events", []))
    events.append({
        "type": decision,
        "payload": {
            "reasoning": result.get("reasoning", ""),
            "escalation_details": result.get("escalation_details", "")
        }
    })
    
    update = {"events": events}
    if decision == "compliance_escalation_required":
        update["needs_human"] = True
        
    return update
