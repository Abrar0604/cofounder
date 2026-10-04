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
