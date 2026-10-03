import pytest
from packages.agents.swarn_agents.orchestrator.logic.conflict import resolve_conflict
from packages.agents.swarn_agents.orchestrator.logic.goals import set_goal
from packages.agents.swarn_agents.orchestrator.nodes.intent import classify_intent
from packages.agents.swarn_agents.orchestrator.nodes.router import choose_next_agent
from packages.agents.swarn_agents.orchestrator.nodes.dispatch import dispatch_agent
from packages.agents.swarn_agents.orchestrator.nodes.events import handle_event_for_replan
from packages.agents.swarn_agents.registry import AGENT_SPECS
from packages.agents.swarn_agents.base.agent_spec import AgentSpec

def test_resolve_conflict():
    res = resolve_conflict("Scale up", "Cut costs")
    assert "Scale up" in res
    assert "Cut costs" in res
    assert "founder input" in res

def test_set_goal():
    res1 = set_goal("v1", {"budget": 5000, "timeline_weeks": 4})
    assert "4 weeks" in res1
    assert "$5000" in res1
    
    res2 = set_goal("v1", {"budget": 1000})
    assert "$1000" in res2
    assert "weeks" not in res2

class MockDecisionResult:
    def __init__(self, choice):
        self.choice = choice

class MockDecisionRuntime:
    def __init__(self, choice):
        self.res = MockDecisionResult(choice)
    async def run(self, *args, **kwargs):
        return self.res

class MockDeps:
    def __init__(self, choice):
        self.decisions = MockDecisionRuntime(choice)

@pytest.mark.asyncio
async def test_classify_intent():
    class MockMsg:
        def __init__(self, t, c):
            self.type = t
            self.content = c
            
    deps = MockDeps("set_goal")
    state = {"messages": [MockMsg("human", "I want to launch")]}
    res = await classify_intent(deps, state)
    assert res["task"] == "set_goal"

@pytest.mark.asyncio
async def test_choose_next_agent():
    # Setup dummy agent spec
    agent_specs = {"market_intel": AgentSpec("market_intel", frozenset(), frozenset(), frozenset(), lambda d: None)}
    
    deps = MockDeps("market_intel")
    state = {"task": "test"}
    res = await choose_next_agent(deps, state, list(agent_specs.keys()))
    assert "market_intel" in res["next_agents"]

@pytest.mark.asyncio
async def test_dispatch_agent():
    state = {"next_agents": ["market_intel", "validation"], "agent_hops": 2}
    res = await dispatch_agent(None, state)
    assert res["active_agent"] == "market_intel"
    assert res["next_agents"] == ["validation"]
    assert res["agent_hops"] == 3

@pytest.mark.asyncio
async def test_handle_event_for_replan():
    agent_specs = {"validation": AgentSpec("validation", frozenset(), frozenset(["market_changed"]), frozenset(), lambda d: None)}
    
    deps = MockDeps("validation")
    state = {"events": [{"type": "market_changed", "payload": {}}], "next_agents": [], "active_agent": None}
    res = await handle_event_for_replan(deps, state, agent_specs)
    
    assert res["next_agents"] == ["validation"]
