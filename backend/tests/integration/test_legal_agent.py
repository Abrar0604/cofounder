import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from packages.agents.swarn_agents.legal.graph import get_spec
from packages.agents.swarn_agents.testing.build_test_deps import build_test_deps
from packages.decisions.ports import Decision

class MockStoreSuccess:
    async def asimilarity_search(self, query, k=3):
        return [
            Document(page_content="Any AI service must comply with GDPR Article 5.", metadata={"citation": "GDPR Art 5"})
        ]

class MockStoreEmpty:
    async def asimilarity_search(self, query, k=3):
        return []

@pytest.mark.asyncio
@patch("packages.agents.swarn_agents.legal.nodes.retrieve.get_legal_vectorstore", return_value=MockStoreSuccess())
async def test_legal_agent_success(mock_get_store):
    jev_script = {
        "answer_or_abstain": Decision(
            question_id="leg-test",
            confidence=0.95,
            reasoning="Based on GDPR Art 5, this is compliant.",
            action="answer"
        )
    }
    
    deps = build_test_deps(None, None, jev_script=jev_script)
    # Give fake settings so DB URL is present
    class DummySettings:
        database_url = "dummy"
    deps = type(deps)(
        engine=deps.engine, redis=deps.redis, settings=DummySettings(),
        registry=deps.registry, policies=deps.policies, decisions=deps.decisions,
        models=deps.models, checkpointer=deps.checkpointer, store=deps.store
    )
    
    spec = get_spec()
    graph = spec.build_graph(deps)
    
    state = {"events": [], "task": "Check GDPR compliance"}
    result = await graph.ainvoke(state)
    
    # Verify retrieved documents reached the decision runtime
    assert len(deps.decisions.received_states) == 1
    use_case, received_state = deps.decisions.received_states[0]
    assert use_case == "answer_or_abstain"
    assert len(received_state.documents) == 1
    assert received_state.documents[0].citation == "GDPR Art 5"
    assert received_state.documents[0].content == "Any AI service must comply with GDPR Article 5."
    
    events = result["events"]
    assert len(events) == 2
    assert events[0]["type"] == "legal_statutes_retrieved"
    assert events[1]["type"] == "legal_advice_provided"
    assert events[1]["payload"]["advice"] == "Based on GDPR Art 5, this is compliant."
    assert "GDPR Art 5" in events[1]["payload"]["citations"]

@pytest.mark.asyncio
@patch("packages.agents.swarn_agents.legal.nodes.retrieve.get_legal_vectorstore", return_value=MockStoreEmpty())
async def test_legal_agent_abstain_empty_docs(mock_get_store):
    jev_script = {}
    deps = build_test_deps(None, None, jev_script=jev_script)
    class DummySettings:
        database_url = "dummy"
    deps = type(deps)(
        engine=deps.engine, redis=deps.redis, settings=DummySettings(),
        registry=deps.registry, policies=deps.policies, decisions=deps.decisions,
        models=deps.models, checkpointer=deps.checkpointer, store=deps.store
    )
    spec = get_spec()
    graph = spec.build_graph(deps)
    
    state = {"events": [], "task": "Check obscure law"}
    result = await graph.ainvoke(state)
    
    events = result["events"]
    assert len(events) == 2
    assert events[0]["type"] == "legal_statutes_retrieved"
    assert events[1]["type"] == "legal_advice_abstained"
    assert events[1]["payload"]["reason"] == "No relevant statutes found"

