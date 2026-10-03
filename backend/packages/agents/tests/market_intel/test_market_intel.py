import pytest
from packages.agents.swarn_agents.market_intel.nodes import gather_intel, run_decision
from packages.agents.swarn_agents.market_intel.tools import search_market_data, fetch_competitor_metrics
from packages.agents.swarn_agents.market_intel.graph import get_spec

class MockDecisionResult:
    def __init__(self, choice):
        self.choice = choice

class MockDecisionRuntime:
    async def run(self, *args, **kwargs):
        return MockDecisionResult("large_tam")

class MockDeps:
    def __init__(self):
        self.decisions = MockDecisionRuntime()

@pytest.mark.asyncio
async def test_gather_intel():
    res = await gather_intel(MockDeps(), {"task": "test query"})
    assert res["events"][0]["type"] == "market_data_gathered"
    
@pytest.mark.asyncio
async def test_run_decision():
    res = await run_decision(MockDeps(), {"events": []})
    assert res["events"][0]["type"] == "market_size_evaluated"
    assert res["events"][0]["payload"]["size"] == "large_tam"

@pytest.mark.asyncio
async def test_tools():
    res = await search_market_data("test")
    assert "error" in res or "results" in res
    
    res2 = await fetch_competitor_metrics("test.com")
    assert "metrics" in res2

def test_spec():
    spec = get_spec()
    assert "search_market_data" in spec.allowed_tools
