import pytest
import json
from packages.agents.swarn_agents.models.model_router import ModelRouter, PolicyViolation
from packages.agents.swarn_agents.models.choose_model_tier import choose_model_tier
from packages.agents.swarn_agents.models.errors import SkipLlm
from packages.agents.swarn_agents.base.compact_context import compact_messages
from packages.agents.swarn_agents.base.interrupt_for_approval import interrupt_for_approval, ApprovalRequired
from packages.observability.swarn_observability.tracing.run_config import run_config
from packages.agents.swarn_agents.testing.fake_chat_model import FakeChatModel
from packages.agents.swarn_agents.base.agent_state import RequestContext
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class MockSettings:
    strong_model = "gemini-1.5-pro"
    cheap_model = "gemini-1.5-flash"
    google_api_key = "dummy_key"

def test_model_router():
    router = ModelRouter(MockSettings())
    strong = router.get_model('strong')
    assert strong.model == "gemini-1.5-pro"
    
    cheap = router.get_model('cheap')
    assert cheap.model == "gemini-1.5-flash"
    
    with pytest.raises(PolicyViolation):
        router.get_model('unknown')

class MockDecisionResult:
    def __init__(self, outcome, choice):
        self.outcome = outcome
        self.choice = choice

class MockDecisionRuntime:
    def __init__(self, outcome, choice):
        self.res = MockDecisionResult(outcome, choice)
    async def run(self, *args, **kwargs):
        return self.res
    async def run_batch(self, use_case, states):
        return [self.res for _ in states]

class MockDeps:
    def __init__(self, outcome, choice):
        self.decisions = MockDecisionRuntime(outcome, choice)

@pytest.mark.asyncio
async def test_choose_model_tier():
    # ESCALATE -> strong
    deps = MockDeps('ESCALATE', 'haiku')
    assert await choose_model_tier(deps, None, None, 'v1', 'task', 'step') == 'strong'
    
    # no_llm_needed -> SkipLlm
    deps = MockDeps('AUTO', 'no_llm_needed')
    with pytest.raises(SkipLlm):
        await choose_model_tier(deps, None, None, 'v1', 'task', 'step')
        
    # haiku -> cheap
    deps = MockDeps('AUTO', 'haiku')
    assert await choose_model_tier(deps, None, None, 'v1', 'task', 'step') == 'cheap'
    
    # sonnet -> strong
    deps = MockDeps('AUTO', 'sonnet')
    assert await choose_model_tier(deps, None, None, 'v1', 'task', 'step') == 'strong'

@pytest.mark.asyncio
async def test_compact_messages():
    class MockMsg:
        def __init__(self, t, c=""):
            self.type = t
            self.content = c
            
    msgs = [MockMsg("system"), MockMsg("human"), MockMsg("ai")] + [MockMsg("ai", f"old {i}") for i in range(10)] + [MockMsg("ai", f"new {i}") for i in range(6)]
    
    # 1 system + 2 old + 10 old + 6 new = 19 messages
    # If we drop 'old' messages based on AUTO drop:
    deps = MockDeps('AUTO', 'drop')
    compacted = await compact_messages(deps, None, None, 'v1', msgs, max_messages=5)
    
    # Should keep system (1), last 6 = 7 messages total
    assert len(compacted) == 7
    assert compacted[0].type == "system"
    assert compacted[-1].content == "new 5"

def test_run_config():
    ctx = RequestContext(tenant_id="tenant-123", user_id="u1", role="admin")
    config = run_config(ctx, "v1", "test_agent", "run1")
    
    metadata = config["metadata"]
    assert "tenant-123" not in metadata.values()
    assert metadata["tenant_id_hash"] != "tenant-123"
    assert len(metadata["tenant_id_hash"]) == 64  # sha256
    assert config["configurable"]["thread_id"] == "run1"

def test_fake_chat_model():
    model = FakeChatModel(['{"score": 90}'])
    
    class FakeSchema:
        @classmethod
        def parse_obj(cls, data):
            return data
            
    chain = model.with_structured_output(FakeSchema)
    res = chain.invoke([{"role": "user", "content": "hi"}])
    assert res == {"score": 90}
    assert len(model.received_messages) == 1

def test_interrupt_for_approval():
    def node1(state):
        try:
            raise ApprovalRequired("app_1", "test_action", "preview")
        except ApprovalRequired as e:
            res = interrupt_for_approval(e)
            return {"status": res.get("decision")}
            
    graph = StateGraph(dict)
    graph.add_node("node1", node1)
    graph.add_edge(START, "node1")
    graph.add_edge("node1", END)
    
    checkpointer = MemorySaver()
    compiled = graph.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "1"}}
    # Run until interrupt
    for _ in compiled.stream({"status": "start"}, config):
        pass
        
    state = compiled.get_state(config)
    assert len(state.tasks) == 1
    assert state.tasks[0].interrupts[0].value["kind"] == "approval"
    
    # Resume
    # LangGraph > 0.1 resume with Command:
    from langgraph.types import Command
    for _ in compiled.stream(Command(resume={"decision": "approved", "approval_id": "app_1"}), config):
        pass
        
    final_state = compiled.get_state(config)
    assert final_state.values["status"] == "approved"

import os
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

@pytest.mark.asyncio
async def test_interrupt_for_approval_postgres():
    # Only run if test db provided
    db_url = os.environ.get("TEST_DATABASE_URL")
    if not db_url:
        pytest.skip("TEST_DATABASE_URL not set")
        
    def node1(state):
        try:
            raise ApprovalRequired("app_2", "test_action", "preview")
        except ApprovalRequired as e:
            res = interrupt_for_approval(e)
            return {"status": res.get("decision")}
            
    graph = StateGraph(dict)
    graph.add_node("node1", node1)
    graph.add_edge(START, "node1")
    graph.add_edge("node1", END)
    
    async with AsyncConnectionPool(conninfo=db_url) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        
        compiled = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "2"}}
        
        async for _ in compiled.astream({"status": "start"}, config):
            pass
            
        state = await compiled.aget_state(config)
        assert len(state.tasks) == 1
        assert state.tasks[0].interrupts[0].value["kind"] == "approval"
        
        from langgraph.types import Command
        async for _ in compiled.astream(Command(resume={"decision": "approved", "approval_id": "app_2"}), config):
            pass
            
        final_state = await compiled.aget_state(config)
        assert final_state.values["status"] == "approved"
