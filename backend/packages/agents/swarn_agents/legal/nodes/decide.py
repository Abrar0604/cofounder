from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.decisions.swarn_decisions.definitions.answer_or_abstain import AnswerOrAbstainState, DocumentInfo

async def answer_or_abstain(deps, state: AgentState) -> dict:
    events = list(state.get("events", []))
    
    retrieved_event = next((e for e in reversed(events) if e["type"] == "legal_statutes_retrieved"), None)
    if not retrieved_event:
        events.append({"type": "legal_advice_abstained", "payload": {"reason": "No statutes retrieved"}})
        return {"events": events}
        
    docs = retrieved_event["payload"].get("documents", [])
    if not docs:
        events.append({"type": "legal_advice_abstained", "payload": {"reason": "No relevant statutes found"}})
        return {"events": events}
        
    doc_infos = [DocumentInfo(content=d["content"], citation=d["citation"]) for d in docs]
    
    d12_state = AnswerOrAbstainState(
        task=state.get("request_text") or state.get("task", ""),
        documents=doc_infos
    )
    
    decision = await deps.decisions.run('answer_or_abstain', d12_state)
    
    if decision.action == "abstain":
        events.append({"type": "legal_advice_abstained", "payload": {"reason": decision.reasoning}})
    else:
        events.append({"type": "legal_advice_provided", "payload": {"advice": decision.reasoning, "citations": [d["citation"] for d in docs]}})
        
    return {"events": events}
