import pytest
from packages.agents.swarn_agents.registry import AGENT_SPECS
from packages.agents.swarn_agents.testing.build_test_deps import build_test_deps
from packages.decisions.ports import Decision

@pytest.mark.asyncio
async def test_specialist_agents_exist():
    expected_agents = ["web", "marketing", "sales", "support"]
    for agent in expected_agents:
        assert agent in AGENT_SPECS
        
@pytest.mark.asyncio
async def test_sales_agent_execution():
    deps = build_test_deps(None, None, jev_script={
        "qualify_lead": Decision(question_id="t1", confidence=1.0, reasoning="High value lead", action="qualified")
    })
    spec = AGENT_SPECS["sales"]
    graph = spec.build_graph(deps)
    result = await graph.ainvoke({"events": [], "task": "Check lead", "messages": [], "tenant_id": "1", "venture_id": "1", "user_id": "1", "role": "1", "run_id": "1", "agent": "sales", "artifacts": [], "needs_human": False})
    assert result["events"][-1]["type"] == "lead_qualified"
    assert result["events"][-1]["payload"]["status"] == "qualified"
    
@pytest.mark.asyncio
async def test_web_agent_execution():
    deps = build_test_deps(None, None, jev_script={
        "define_landing_page": Decision(question_id="t2", confidence=1.0, reasoning="Modern SaaS", action="defined")
    })
    spec = AGENT_SPECS["web"]
    graph = spec.build_graph(deps)
    result = await graph.ainvoke({"events": [], "task": "Make a page", "messages": [], "tenant_id": "1", "venture_id": "1", "user_id": "1", "role": "1", "run_id": "1", "agent": "web", "artifacts": [], "needs_human": False})
    assert result["events"][-1]["type"] == "landing_page_specs_defined"
