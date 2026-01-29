from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import uuid
import datetime
import logging
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from src.common.services.websocket_manager import manager
from src.common.agents.registry import get_chat_agent
from src.api_server.agents.chat.run import run_chat_stream
from src.common.database import get_db
from src.common.repos.chat import UserMessageRepository
from src.api_server.api.auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()

class UserMessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repo = UserMessageRepository(db)
    messages = repo.get_messages_by_user(user_id)
    return messages

@router.post("/messages")
async def post_user_message(
    request: UserMessageRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    chat_agent = get_chat_agent()
    message_repo = UserMessageRepository(db)
    
    user_id_str = str(user_id)
    # Using user_id_str as thread_id for one-conversation-per-user
    thread_id = user_id_str

    # Save user message to database
    message_repo.add_message(
        user_id=user_id,
        role="user",
        content=request.message
    )

    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id_str
        }
    }
    inputs = {
        "messages": [HumanMessage(content=request.message)],
        "user_id": user_id_str
    }
    
    # Broadcast thinking state
    await manager.send_to_user(user_id_str, {
        "type": "lumi_thinking"
    })

    full_content = ""
    # Use run_chat_stream to capture tokens and trigger optimizer
    async for chunk_data in run_chat_stream(chat_agent, inputs, config):
        chunk, metadata = chunk_data
        
        if isinstance(chunk, AIMessage) and chunk.content:
            content_chunk = chunk.content
            if isinstance(content_chunk, list):
                # Handle cases where content might be a list of dicts (e.g. tool calls)
                # For a simple chat agent it's usually just a string
                pass 
            else:
                full_content += content_chunk
                await manager.send_to_user(user_id_str, {
                    "type": "token",
                    "content": content_chunk
                })
        elif hasattr(chunk, "tool_calls") and chunk.tool_calls:
             # It's a message with tool calls, but maybe no content yet
             pass
    
    # Broadcast done event
    await manager.send_to_user(user_id_str, {
        "type": "done"
    })

    # Save assistant response to database
    message_repo.add_message(
        user_id=user_id,
        role="assistant",
        content=full_content
    )
    
    return {
        "type": "chat_response",
        "content": full_content,
        "thread_id": thread_id
    }
