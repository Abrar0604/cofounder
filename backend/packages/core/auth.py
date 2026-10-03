import jwt
import httpx
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from packages.core.config import settings

security = HTTPBearer()

import time

# Cache for JWKS
_jwks_cache = None
_jwks_cache_time = 0
JWKS_CACHE_TTL = 3600  # 1 hour

async def get_jwks(force_refresh=False):
    global _jwks_cache, _jwks_cache_time
    now = time.time()
    
    if not force_refresh and _jwks_cache and (now - _jwks_cache_time < JWKS_CACHE_TTL):
        return _jwks_cache
    
    # Normally we'd extract the domain from the publishable key or secret
    # Or just require the user to configure CLERK_JWKS_URL or CLERK_DOMAIN
    # A standard Clerk setup allows fetching JWKS without auth if we know the domain,
    # but the secret key is required for some verification.
    if not settings.clerk_secret_key:
        raise HTTPException(status_code=500, detail="Clerk secret key not configured")
        
    # We can fetch the JWKS using the secret key (Clerk Backend API)
    async with httpx.AsyncClient() as client:
        # For a more robust approach in production, use the clerk-backend-api SDK
        response = await client.get(
            "https://api.clerk.com/v1/jwks",
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch JWKS from Clerk")
        _jwks_cache = response.json()
        _jwks_cache_time = now
        return _jwks_cache

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    
    try:
        # 1. Get unverified header to find kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        # 2. Fetch JWKS
        jwks = await get_jwks()
        
        # 3. Find matching key
        def find_key(jwks_dict):
            for key in jwks_dict.get("keys", []):
                if key["kid"] == kid:
                    return {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            return {}
            
        rsa_key = find_key(jwks)
        
        if not rsa_key:
            # Refresh JWKS and retry once
            jwks = await get_jwks(force_refresh=True)
            rsa_key = find_key(jwks)
            
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Invalid token: Key not found")
            
        # 4. Decode token
        # Normally you verify audience and issuer as well.
        payload = jwt.decode(
            token,
            jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key),
            algorithms=["RS256"],
            options={"verify_aud": False, "verify_iss": False}
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
