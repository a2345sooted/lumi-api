from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import datetime
from pydantic import BaseModel, ConfigDict
from src.common.database import get_db
from src.api_server.api.auth import get_current_user_id
from src.common.repos.users import UserRepository
from src.common.repos.chat import UserMessageRepository
from src.common.services.push_notifications import send_expo_push_notifications
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class UserMeResponse(BaseModel):
    id: uuid.UUID
    sub: str
    created_at: datetime.datetime
    push_token: Optional[str] = None
    messages: List[MessageResponse]

    model_config = ConfigDict(from_attributes=True)

class PushTokenRequest(BaseModel):
    push_token: str

@router.get("/me", response_model=UserMeResponse)
async def get_user_info(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user_uuid = uuid.UUID(user_id)
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_uuid)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    message_repo = UserMessageRepository(db)
    messages = message_repo.get_messages_by_user(user_uuid)
    
    return {
        "id": user.id,
        "sub": user.sub,
        "created_at": user.created_at,
        "push_token": user.push_token,
        "messages": messages
    }

@router.post("/push-token")
async def register_push_token(
    request: PushTokenRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user_uuid = uuid.UUID(user_id)
    user_repo = UserRepository(db)
    user = user_repo.update_push_token(user_uuid, request.push_token)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"status": "success", "message": "Push token updated"}

@router.post("/test-push")
async def test_push_notification(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user_uuid = uuid.UUID(user_id)
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_uuid)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.push_token:
        raise HTTPException(status_code=400, detail="User has no push token registered")
        
    send_expo_push_notifications(
        push_tokens=[user.push_token],
        message="This is a test notification from Lumi!",
        title="Test Notification",
        data={"test": True}
    )
    
    return {"status": "success", "message": "Test notification sent"}
