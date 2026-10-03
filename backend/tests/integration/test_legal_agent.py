import pytest
from packages.agents.swarn_agents.legal.graph import get_spec
from packages.agents.swarn_agents.testing.build_test_deps import build_test_deps
from packages.decisions.ports import Decision

@pytest.mark.asyncio
async def test_legal_agent_success():
    jev_script = {
        "answer_or_abstain": Decision(
            question_id="leg-test",
            confidence=0.95,
            reasoning="Based on GDPR Art 5, this is compliant.",
            action="answer"
        )
    }
    
    deps = build_test_deps(None, None, jev_script=jev_script)
    spec = get_spec()
    graph = spec.build_graph(deps)
    
    state = {"events": [], "task": "Check GDPR compliance"}
    result = await graph.ainvoke(state)
    
    events = result["events"]
    assert len(events) == 2
    assert events[0]["type"] == "legal_statutes_retrieved"
    assert events[1]["type"] == "legal_advice_provided"
    assert events[1]["payload"]["advice"] == "Based on GDPR Art 5, this is compliant."

@pytest.mark.asyncio
async def test_legal_agent_abstain():
    jev_script = {
        "answer_or_abstain": Decision(
            question_id="leg-test2",
            confidence=0.4,
            reasoning="Missing sufficient citation context to answer definitively.",
            action="abstain"
        )
    }
    
    deps = build_test_deps(None, None, jev_script=jev_script)
    spec = get_spec()
    graph = spec.build_graph(deps)
    
    state = {"events": [], "task": "Check obscure law"}
    result = await graph.ainvoke(state)
    
    events = result["events"]
    assert len(events) == 2
    assert events[0]["type"] == "legal_statutes_retrieved"
    assert events[1]["type"] == "legal_advice_abstained"
    assert events[1]["payload"]["reason"] == "Missing sufficient citation context to answer definitively."
