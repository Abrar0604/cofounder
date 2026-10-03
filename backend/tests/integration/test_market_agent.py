import pytest
from packages.agents.swarn_agents.market_intel.graph import get_spec
from packages.agents.swarn_agents.testing.build_test_deps import build_test_deps
from packages.decisions.ports import Decision

@pytest.mark.asyncio
async def test_market_intel_success():
    jev_script = {
        "evaluate_market_size": Decision(
            question_id="test",
            confidence=0.9,
            reasoning="Looks good",
            action="large_tam"
        )
    }
    
    from unittest.mock import patch
    
    with patch("packages.agents.swarn_agents.market_intel.nodes.search_market_data", return_value={"results": ["data1", "data2"]}):
        deps = build_test_deps(None, None, jev_script=jev_script)
        spec = get_spec()
        graph = spec.build_graph(deps)
        
        # Input event: user_request
        state = {"events": [], "task": "analyze AI market"}
        
        result = await graph.ainvoke(state)
        
        events = result["events"]
        assert len(events) == 2
    assert events[0]["type"] == "market_data_gathered"
    assert events[1]["type"] == "market_size_evaluated"
    assert events[1]["payload"]["size"] == "large_tam"

@pytest.mark.asyncio
async def test_market_intel_bad_input():
    # If the search data fails (has "error"), it should halt and not produce market_size_evaluated
    from unittest.mock import patch
    
    with patch("packages.agents.swarn_agents.market_intel.nodes.search_market_data", return_value={"error": "API key missing"}):
        deps = build_test_deps(None, None, jev_script={})
        spec = get_spec()
        graph = spec.build_graph(deps)
        
        state = {"events": [], "task": "analyze AI market"}
        result = await graph.ainvoke(state)
        
        events = result["events"]
        assert len(events) == 1
        assert events[0]["type"] == "market_data_gathered"
        assert "error" in events[0]["payload"]
        # No market_size_evaluated event because it halted correctly
