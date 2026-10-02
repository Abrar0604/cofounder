import hmac
import hashlib
import os
import time
from fastapi import HTTPException, Request

# We will load from env directly or through settings
GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
STRIPE_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not GITHUB_SECRET or not STRIPE_SECRET:
    raise RuntimeError("GITHUB_WEBHOOK_SECRET and STRIPE_WEBHOOK_SECRET must be set in the environment.")

async def verify_github_signature(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    body = await request.body()
    expected_signature = "sha256=" + hmac.new(GITHUB_SECRET.encode(), body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

async def verify_stripe_signature(request: Request):
    signature_header = request.headers.get("Stripe-Signature")
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    body = await request.body()
    
    try:
        # Stripe-Signature: t=1614992683,v1=5257a869e7ecebeda32affa62cecdeefa996020db209e51c8903c73493db616f
        parts = dict(part.split("=", 1) for part in signature_header.split(","))
        timestamp = parts.get("t")
        sig = parts.get("v1")
        
        if not timestamp or not sig:
            raise ValueError()
            
        timestamp_int = int(timestamp)
        if time.time() - timestamp_int > 300: # 5 minutes tolerance
            raise HTTPException(status_code=401, detail="Timestamp outside tolerance")
            
        signed_payload = f"{timestamp}.{body.decode('utf-8')}"
        expected_sig = hmac.new(STRIPE_SECRET.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(sig, expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=401, detail="Invalid signature format")
