import hmac
import hashlib
import os
import time
from fastapi import HTTPException, Request

# We will load from env directly or through settings
META_SECRET = os.getenv("META_WEBHOOK_SECRET")
STRIPE_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not META_SECRET or not STRIPE_SECRET:
    raise RuntimeError("META_WEBHOOK_SECRET and STRIPE_WEBHOOK_SECRET must be set in the environment.")

async def verify_meta_signature(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    body = await request.body()
    expected_signature = "sha256=" + hmac.new(META_SECRET.encode(), body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

async def verify_stripe_signature(request: Request):
    signature_header = request.headers.get("Stripe-Signature")
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    body = await request.body()
    
    try:
        # Stripe-Signature: t=1614992683,v1=5257a869e7ecebeda32affa62cecdeefa996020db209e51c8903c73493db616f
        parts = [part.split("=", 1) for part in signature_header.split(",") if "=" in part]
        timestamp = next((v for k, v in parts if k == "t"), None)
        sigs = [v for k, v in parts if k == "v1"]
        
        if not timestamp or not sigs:
            raise ValueError()
            
        timestamp_int = int(timestamp)
        if time.time() - timestamp_int > 300: # 5 minutes tolerance
            raise HTTPException(status_code=401, detail="Timestamp outside tolerance")
            
        signed_payload = f"{timestamp}.{body.decode('utf-8')}"
        expected_sig = hmac.new(STRIPE_SECRET.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
        
        if not any(hmac.compare_digest(sig, expected_sig) for sig in sigs):
            raise HTTPException(status_code=401, detail="Invalid signature")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=401, detail="Invalid signature format")
