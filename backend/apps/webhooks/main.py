from fastapi import FastAPI, Depends, Request, HTTPException
from typing import Dict, Any
from apps.webhooks.verify import verify_meta_signature, verify_stripe_signature
from packages.core.bus import EventBus
import os

bus = EventBus(os.getenv("REDIS_URL", "redis://localhost:6379"))

app = FastAPI(title="Swarn Webhooks API")

@app.post("/meta", dependencies=[Depends(verify_meta_signature)])
async def meta_webhook(request: Request, payload: Dict[str, Any]):
    event_payload = {
        "source": "meta",
        "data": payload
    }
    receivers = await bus.publish("inbound_webhooks", "meta_event", event_payload)
    if receivers == 0:
        raise HTTPException(status_code=503, detail="No active subscribers to process webhook")
    return {"status": "success"}

@app.get("/meta")
async def meta_challenge(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == os.getenv("META_VERIFY_TOKEN"):
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=challenge)
    raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/stripe", dependencies=[Depends(verify_stripe_signature)])
async def stripe_webhook(request: Request, payload: Dict[str, Any]):
    event_payload = {
        "source": "stripe",
        "data": payload
    }
    receivers = await bus.publish("inbound_webhooks", "stripe_event", event_payload)
    if receivers == 0:
        raise HTTPException(status_code=503, detail="No active subscribers to process webhook")
    return {"status": "success"}
