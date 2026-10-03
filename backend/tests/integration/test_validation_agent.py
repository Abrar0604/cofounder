import pytest
from packages.agents.swarn_agents.validation.graph import get_spec
from packages.agents.swarn_agents.testing.build_test_deps import build_test_deps
from packages.decisions.ports import Decision

@pytest.mark.asyncio
async def test_validation_success():
    jev_script = {
        "score_viability": Decision(
            question_id="val-test",
            confidence=0.9,
            reasoning="Viable startup idea",
            action="high"
        )
    }
    deps = build_test_deps(None, None, jev_script=jev_script)
    spec = get_spec()
    graph = spec.build_graph(deps)
    
    # We must seed market_size_evaluated since it consumes it
    state = {
        "events": [
            {"type": "market_size_evaluated", "payload": {"size": "large"}}
        ],
        "task": "healthcare"
    }
    
    result = await graph.ainvoke(state)
    
    events = result["events"]
    assert len(events) == 3 # 1 input + 2 emitted
    assert events[1]["type"] == "compliance_checked"
    assert events[2]["type"] == "viability_scored"
    assert events[2]["payload"]["score"] == "high"

@pytest.mark.asyncio
async def test_validation_bad_input():
    # If missing earlier events, check it handles it gracefully
    jev_script = {
        "score_viability": Decision(
            question_id="val-test-bad",
            confidence=0.9,
            reasoning="Missing market eval",
            action="low"
        )
    }
    deps = build_test_deps(None, None, jev_script=jev_script)
    spec = get_spec()
    graph = spec.build_graph(deps)
    
    state = {"events": [], "task": "unknown"}
    result = await graph.ainvoke(state)
    
    events = result["events"]
    assert len(events) == 2
    assert events[0]["type"] == "compliance_checked"
    assert events[1]["type"] == "viability_scored"
    assert events[1]["payload"]["score"] == "low"
