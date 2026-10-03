import pytest
from packages.agents.swarn_agents.validation.nodes import validate_model, score_viability_node
from packages.agents.swarn_agents.validation.tools import check_compliance_rules
from packages.agents.swarn_agents.validation.graph import get_spec

class MockDecisionResult:
    def __init__(self, choice):
        self.choice = choice

class MockDecisionRuntime:
    async def run(self, *args, **kwargs):
        return MockDecisionResult("high")

class MockDeps:
    def __init__(self):
        self.decisions = MockDecisionRuntime()

@pytest.mark.asyncio
async def test_validate_model():
    res = await validate_model(MockDeps(), {})
    assert res["events"][0]["type"] == "compliance_checked"

@pytest.mark.asyncio
async def test_score_viability():
    res = await score_viability_node(MockDeps(), {})
    assert res["events"][0]["type"] == "viability_scored"
    assert res["events"][0]["payload"]["score"] == "high"

def test_tools():
    res = check_compliance_rules("finance")
    assert "KYC" in res["rules"]

def test_spec():
    spec = get_spec()
    assert "check_compliance_rules" in spec.allowed_tools
