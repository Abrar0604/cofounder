import pytest
from httpx import AsyncClient, ASGITransport
import hmac
import hashlib
import os

os.environ["META_WEBHOOK_SECRET"] = "dummy_meta"
os.environ["STRIPE_WEBHOOK_SECRET"] = "dummy_stripe"

from apps.webhooks.main import app as webhook_app
from apps.webhooks.verify import META_SECRET
from apps.api.routes.approvals import router as approvals_router
from fastapi import FastAPI

# Dummy Main API for testing E2E approvals
api_app = FastAPI()
api_app.include_router(approvals_router)

@pytest.mark.asyncio
async def test_meta_webhook_flow():
    # Simulate a webhook from Meta
    payload = b'{"object": "whatsapp_business_account", "entry": [{"id": "123", "changes": [{"value": {"messages": [{"text": {"body": "hello"}}]}}]}]}'
    signature = "sha256=" + hmac.new(META_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    
    from unittest.mock import patch
    with patch("apps.webhooks.main.bus.publish", return_value=1) as mock_publish:
        async with AsyncClient(transport=ASGITransport(app=webhook_app), base_url="http://test") as client:
            response = await client.post(
                "/meta",
                content=payload,
                headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"}
            )
            assert response.status_code == 200
            assert response.json() == {"status": "success"}
            
            # Assert exact event-bus publication tuple
            import json
            expected_payload = {
                "source": "meta",
                "data": json.loads(payload)
            }
            mock_publish.assert_called_once_with("inbound_webhooks", "meta_event", expected_payload)

@pytest.mark.asyncio
async def test_stripe_webhook_flow():
    from apps.webhooks.verify import STRIPE_SECRET
    import time
    
    payload = b'{"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_123"}}}'
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    sig = hmac.new(STRIPE_SECRET.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    signature_header = f"t={timestamp},v1={sig}"
    
    from unittest.mock import patch
    with patch("apps.webhooks.main.bus.publish", return_value=1) as mock_publish:
        async with AsyncClient(transport=ASGITransport(app=webhook_app), base_url="http://test") as client:
            response = await client.post(
                "/stripe",
                content=payload,
                headers={"Stripe-Signature": signature_header, "Content-Type": "application/json"}
            )
            assert response.status_code == 200
            assert response.json() == {"status": "success"}
            
            # Assert exact event-bus publication tuple
            import json
            expected_payload = {
                "source": "stripe",
                "data": json.loads(payload)
            }
            mock_publish.assert_called_once_with("inbound_webhooks", "stripe_event", expected_payload)
        
@pytest.mark.asyncio
async def test_approval_flow():
    # Simulate approving a thread
    async with AsyncClient(transport=ASGITransport(app=api_app), base_url="http://test") as client:
        response = await client.post("/approvals/thread_123/approve", json={"data": {"decision": "yes"}})
        assert response.status_code == 200
        assert response.json()["status"] == "approved"
        assert response.json()["thread_id"] == "thread_123"

@pytest.mark.asyncio
async def test_full_system_e2e():
    from packages.brain.services.brain_service import BrainService
    from packages.agents.swarn_agents.orchestrator.graph import build_orchestrator_graph
    from packages.agents.swarn_agents.testing.build_test_deps import build_test_deps
    from packages.decisions.ports import Decision
    import json
    
    # 1. Simulate a user creating a venture
    brain = BrainService()
    brain.create_venture("v1", {"name": "E2E Venture", "market": "AI"})
    assert "v1" in brain.ventures
    
    # 2. Simulate Agents processing it
    from langchain_core.messages import AIMessage
    
    class DummyModel:
        async def ainvoke(self, *args, **kwargs):
            return AIMessage(content="Summary")
            
    deps = build_test_deps(None, None, scripted_models={"cheap": DummyModel()}, jev_script={
        "founder_intent": Decision(question_id="q1", confidence=1.0, reasoning="User wants to research", action="market_intel"),
        "route_supervisor": Decision(question_id="q2", confidence=1.0, reasoning="Route to market_intel", action="market_intel"),
        "fan_out_event": Decision(question_id="q3", confidence=1.0, reasoning="No fan out needed here", action="none")
    })
    # Attach our brain instance so we can inspect it later
    deps = type(deps)(
        engine=deps.engine, redis=deps.redis, settings=deps.settings,
        registry=deps.registry, policies=deps.policies, decisions=deps.decisions,
        models=deps.models, checkpointer=deps.checkpointer, store=brain
    )
    
    from packages.agents.swarn_agents.registry import AGENT_SPECS
    graph = build_orchestrator_graph(deps, AGENT_SPECS)
    
    state = {
        "messages": [("human", "Let's research the AI market.")],
        "tenant_id": "t1", "venture_id": "v1", "user_id": "u1", "role": "admin",
        "run_id": "r1", "agent": "orchestrator", "task": "",
        "artifacts": [], "events": [], "needs_human": False, "error": None,
        "next_agents": [], "agent_hops": 0
    }
    result = await graph.ainvoke(state)
    assert result["summary"] == "Summary"
    assert result["active_agent"] == "market_intel"
    
    # 3. Simulate Webhook triggering an update (Sales Agent Lead Qualify)
    payload = b'{"object": "whatsapp_business_account", "entry": [{"id": "123", "changes": [{"value": {"messages": [{"text": {"body": "qualify me"}}]}}]}]}'
    signature = "sha256=" + hmac.new(META_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    
    from unittest.mock import patch
    
    async def simulated_webhook_worker(channel, event_type, data):
        # The worker would receive the message and use brain service to process it
        brain.add_constraint("c1", {"source": "webhook", "data": data})
        return 1

    with patch("apps.webhooks.main.bus.publish", side_effect=simulated_webhook_worker) as mock_publish:
        async with AsyncClient(transport=ASGITransport(app=webhook_app), base_url="http://test") as client:
            response = await client.post(
                "/meta",
                content=payload,
                headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"}
            )
            assert response.status_code == 200
            
    # 4. Verify Database State
    assert "c1" in brain.constraints
    assert brain.constraints["c1"]["source"] == "webhook"
    events = brain.get_events()
    assert len(events) == 2
    assert events[0].event_type == "venture.created"
    assert events[1].event_type == "constraint.added"
