import hmac
import hashlib
from fastapi import HTTPException, Request

SECRET_KEY = b"dummy_secret_key"

async def verify_signature(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    body = await request.body()
    expected_signature = "sha256=" + hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
