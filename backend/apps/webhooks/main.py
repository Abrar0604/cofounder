from fastapi import FastAPI, Depends, Request
from typing import Dict, Any
from contextlib import asynccontextmanager
from apps.webhooks.verify import verify_meta_signature, verify_stripe_signature
from packages.core.bus import EventBus
import os

bus = EventBus(os.getenv("REDIS_URL", "redis://localhost:6379"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bus.connect()
    yield
    await bus.close()

app = FastAPI(title="Swarn Webhooks API", lifespan=lifespan)

@app.post("/meta", dependencies=[Depends(verify_meta_signature)])
async def meta_webhook(request: Request, payload: Dict[str, Any]):
    # Process Meta webhook payload and publish to event bus
    # Note: Meta often requires a GET /meta endpoint for challenge verification too.
    # Assuming this is just the event POST.
    event_payload = {
        "source": "meta",
        "data": payload
    }
    # Using a generic global channel for inbound webhooks, or route by tenant
    await bus.publish("inbound_webhooks", "meta_event", event_payload)
    return {"status": "success"}

@app.get("/meta")
async def meta_challenge(request: Request):
    # Meta webhook challenge response
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == os.getenv("META_VERIFY_TOKEN", "dummy_token"):
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=challenge)
    from fastapi import HTTPException
    raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/stripe", dependencies=[Depends(verify_stripe_signature)])
async def stripe_webhook(request: Request, payload: Dict[str, Any]):
    # Process stripe webhook payload
    event_payload = {
        "source": "stripe",
        "data": payload
    }
    await bus.publish("inbound_webhooks", "stripe_event", event_payload)
    return {"status": "success"}
