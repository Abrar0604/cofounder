from fastapi import FastAPI, Depends, Request
from typing import Dict, Any
from apps.webhooks.verify import verify_github_signature, verify_stripe_signature

app = FastAPI(title="Swarn Webhooks API")

@app.post("/github", dependencies=[Depends(verify_github_signature)])
async def github_webhook(request: Request, payload: Dict[str, Any]):
    # Process github webhook payload
    print(f"Received verified github webhook: {payload.get('action')}")
    return {"status": "success"}

@app.post("/stripe", dependencies=[Depends(verify_stripe_signature)])
async def stripe_webhook(request: Request, payload: Dict[str, Any]):
    # Process stripe webhook payload
    print(f"Received verified stripe webhook: {payload.get('type')}")
    return {"status": "success"}
