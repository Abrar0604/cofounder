import pytest
from packages.agents.swarn_agents.financial.graph import get_spec
from packages.agents.swarn_agents.testing.build_test_deps import build_test_deps
from packages.decisions.ports import Decision

@pytest.mark.asyncio
async def test_financial_success():
    jev_script = {
        "assess_burn_rate": Decision(
            question_id="fin-test",
            confidence=0.9,
            reasoning="Burn rate is acceptable",
            action="healthy"
        )
    }
    
    from unittest.mock import patch
    
    with patch("packages.agents.swarn_agents.financial.nodes.check_spend", return_value={"total_spent": 100, "budget": 1000, "burn_rate_per_week": 10}):
        deps = build_test_deps(None, None, jev_script=jev_script)
        spec = get_spec()
        graph = spec.build_graph(deps)
        
        state = {"events": [], "venture_id": "v123"}
        
        result = await graph.ainvoke(state)
        
        events = result["events"]
        assert len(events) == 2
    assert events[0]["type"] == "financials_reviewed"
    assert events[1]["type"] == "burn_rate_assessed"
    assert events[1]["payload"]["status"] == "healthy"

@pytest.mark.asyncio
async def test_financial_bad_input():
    from unittest.mock import patch
    
    with patch("packages.agents.swarn_agents.financial.nodes.check_spend", return_value={"error": "Not found"}):
        deps = build_test_deps(None, None, jev_script={})
        spec = get_spec()
        graph = spec.build_graph(deps)
        
        state = {"events": [], "venture_id": "v-bad"}
        result = await graph.ainvoke(state)
        
        events = result["events"]
        assert len(events) == 2
        assert events[0]["type"] == "financials_reviewed"
        assert events[1]["type"] == "burn_rate_assessed"
        assert events[1]["payload"]["status"] == "unknown" # Halts or returns unknown on bad data
