import pytest
from httpx import AsyncClient, ASGITransport
import hmac
import hashlib
from apps.webhooks.main import app as webhook_app
from apps.webhooks.verify import SECRET_KEY
from apps.api.routes.approvals import router as approvals_router
from fastapi import FastAPI

# Dummy Main API for testing E2E approvals
api_app = FastAPI()
api_app.include_router(approvals_router)

@pytest.mark.asyncio
async def test_webhook_flow():
    # Simulate a webhook from GitHub
    payload = b'{"action": "opened", "issue": {"title": "Test Issue"}}'
    signature = "sha256=" + hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()
    
    async with AsyncClient(transport=ASGITransport(app=webhook_app), base_url="http://test") as client:
        response = await client.post(
            "/github",
            content=payload,
            headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"}
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        
@pytest.mark.asyncio
async def test_approval_flow():
    # Simulate approving a thread
    async with AsyncClient(transport=ASGITransport(app=api_app), base_url="http://test") as client:
        response = await client.post("/approvals/thread_123/approve", json={"data": {"decision": "yes"}})
        assert response.status_code == 200
        assert response.json()["status"] == "approved"
        assert response.json()["thread_id"] == "thread_123"
