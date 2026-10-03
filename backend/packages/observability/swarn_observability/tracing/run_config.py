import hashlib
import os

def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def run_config(
    ctx, 
    venture_id: str, 
    agent: str, 
    thread_id: str, 
    channel: str = 'web', 
    extra_tags: list[str] | None = None
) -> dict:
    tags = [f"agent:{agent}", f"channel:{channel}"]
    if extra_tags:
        tags.extend(extra_tags)
        
    env = os.getenv("APP_ENV", "development")
    
    # Ensure no raw PII in metadata/tags!
    hashed_tenant = stable_hash(ctx.tenant_id) if ctx.tenant_id else "system"
    
    return {
        "configurable": {
            "thread_id": thread_id,
        },
        "tags": tags,
        "metadata": {
            "tenant_id_hash": hashed_tenant,
            "venture_id": venture_id,
            "agent": agent,
            "channel": channel,
            "environment": env,
            "run_id": thread_id  # Keep for backwards compatibility if needed
        },
        "recursion_limit": 40
    }
