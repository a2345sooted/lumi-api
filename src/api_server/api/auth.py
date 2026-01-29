from fastapi import Security, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
import os
import requests
from jose import jwt, JWTError

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

# Cache for JWKS
_jwks = None

def get_jwks():
    global _jwks
    if _jwks is None:
        try:
            jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
            _jwks = requests.get(jwks_url).json()
        except Exception as e:
            logger.error(f"Error fetching JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not verify authentication token"
            )
    return _jwks

def verify_token(token: str) -> str:
    """Verifies the token with Auth0 and returns the sub (user_id)."""
    # If Auth0 is not configured, we shouldn't continue
    if not AUTH0_DOMAIN:
        logger.error("AUTH0_DOMAIN not set")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication configuration missing"
        )

    # Try decoding as JWT first
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") == "RS256":
            jwks = get_jwks()
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=AUTH0_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload["sub"]
        else:
            logger.debug(f"Token algorithm is {header.get('alg')}, not RS256. Trying /userinfo fallback.")
    except Exception as e:
        logger.debug(f"Token is not a standard JWT or header decode failed: {e}. Trying /userinfo fallback.")

    # Fallback: Treat as opaque token and call /userinfo
    try:
        userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
        response = requests.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            user_data = response.json()
            return user_data["sub"]
        else:
            logger.error(f"Auth0 /userinfo failed with status {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token (opaque token verification failed)",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Unexpected error during /userinfo verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> str:
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Auth token provided: {token}")
    return verify_token(token)

async def get_ws_user_id(token: Optional[str] = Query(None)) -> str:
    """
    Extracts user ID for WebSocket connections from a query parameter.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )
    
    logger.debug(f"WS Auth token provided: {token}")
    return verify_token(token)
