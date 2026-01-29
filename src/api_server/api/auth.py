from fastapi import Security, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

import os

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

# Hardcoded fake user IDs for mapping tokens to users
TOKEN_TO_USER_MAP = {
    "user-1-token": "user_1_2t9R2fX3Q6V8Z9J0C1B4A5D6E1",
    "user-2-token": "user_2_4802sklje6V8Z9J0C1B4A5D6E2",
    "user-3-token": "user_3_m9P5nB7vX1L4K2J8H5G3F1D0S9",
    "user-4-token": "user_4_qW8eR3tY7uI0oP2aS5dF6gH1jK",
}

async def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> str:
    # We log this for debugging purposes during development
    token = credentials.credentials if credentials else None
    if token:
        logger.debug(f"Auth token provided: {token[:10]}...")
        if token in TOKEN_TO_USER_MAP:
            return TOKEN_TO_USER_MAP[token]
    
    # Default fallback
    return "user_default_zX9cV8bN7mQ1wE2r3tY4u5i6o7"

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
    
    if token in TOKEN_TO_USER_MAP:
        return TOKEN_TO_USER_MAP[token]
    
    # Default fallback for any other token during fake auth phase
    return DEFAULT_FAKE_USER_ID
