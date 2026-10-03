import pytest
from packages.agents.swarn_agents.financial.nodes import review_financials, assess_burn
from packages.agents.swarn_agents.financial.tools import check_spend, simulate_revenue_model
from packages.agents.swarn_agents.financial.graph import get_spec

class MockDecisionResult:
    def __init__(self, choice):
        self.choice = choice

class MockDecisionRuntime:
    async def run(self, *args, **kwargs):
        return MockDecisionResult("safe")

class MockDeps:
    def __init__(self):
        self.decisions = MockDecisionRuntime()

@pytest.mark.asyncio
async def test_review_financials():
    res = await review_financials(MockDeps(), {"venture_id": "v1"})
    assert res["events"][0]["type"] == "financials_reviewed"
    assert "total_spent" in res["events"][0]["payload"]
    
@pytest.mark.asyncio
async def test_assess_burn():
    # Setup initial state with a review event
    state = {
        "events": [
            {"type": "financials_reviewed", "payload": {"total_spent": 1000, "budget": 5000, "burn_rate_per_week": 100}}
        ]
    }
    res = await assess_burn(MockDeps(), state)
    
    assert res["events"][1]["type"] == "burn_rate_assessed"
    assert res["events"][1]["payload"]["status"] == "safe"

@pytest.mark.asyncio
async def test_tools():
    spend = await check_spend("v1")
    assert spend["budget"] == 5000.00
    
    missing_spend = await check_spend("missing")
    assert "error" in missing_spend
    
    rev = await simulate_revenue_model({"price": 10, "users": 100, "growth_rate": 1.1})
    assert rev["months"] == 12
    assert rev["final_mrr"] > 1000
    
    bad_rev = await simulate_revenue_model({"price": -10, "users": 100, "growth_rate": 1.1})
    assert "error" in bad_rev

def test_spec():
    spec = get_spec()
    assert "check_spend" in spec.allowed_tools
