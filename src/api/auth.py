from fastapi import Security, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

# Hardcoded fake user ID for now
FAKE_USER_ID = "user_2t9R2fX3Q6V8Z9J0C1B4A5D6E7"

async def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> str:
    # We log this for debugging purposes during development
    if credentials:
        logger.debug(f"Auth token provided: {credentials.credentials[:10]}...")
    
    # No matter what the token, return the fake user id
    # We'll add actual JWT stuff later
    return FAKE_USER_ID

async def get_ws_user_id(token: Optional[str] = Query(None)) -> str:
    """
    Extracts user ID for WebSocket connections from a query parameter.
    If no token is provided, raises an HTTPException which FastAPI
    handles for WebSockets by rejecting the connection with 403.
    """
    if not token:
        # FastAPI handles HTTPException in WebSocket dependencies by returning 403 Forbidden
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )
    
    logger.debug(f"WS Auth token provided: {token[:10]}...")
    
    # Returning the same hardcoded ID for now
    return FAKE_USER_ID
