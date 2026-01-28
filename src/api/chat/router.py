from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import uuid
import datetime
import logging
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from src.api.websockets.manager import manager
from src.agents.registry import get_chat_agent
from src.database import get_db
from src.repos.chat import ConversationRepository, MessageRepository
from src.api.auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()

class UserMessageRequest(BaseModel):
    message: str

class CreateConversationResponse(BaseModel):
    id: str

class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str

    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

@router.post("/conversations", response_model=CreateConversationResponse)
async def create_conversation(
    user_id: str = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    repo = ConversationRepository(db)
    conversation = repo.create(user_id=user_id)
    return {"id": str(conversation.id)}

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    repo = ConversationRepository(db)
    conversations = repo.list_all(user_id=user_id)
    return conversations

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str, 
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repo = MessageRepository(db)
    conv_repo = ConversationRepository(db)
    try:
        conv_id = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    
    conversation = conv_repo.get_by_id(conv_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = repo.get_messages_by_conversation(conv_id)
    return messages

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str, 
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repo = ConversationRepository(db)
    try:
        conv_id = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    
    conversation = repo.get_by_id(conv_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    success = repo.delete(conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "success", "message": "Conversation deleted"}

@router.post("/conversations/{conversation_id}/messages")
async def post_user_message(
    conversation_id: str, 
    request: UserMessageRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    chat_agent = get_chat_agent()
    message_repo = MessageRepository(db)
    
    try:
        conv_id = uuid.UUID(conversation_id)
        
        # Check if conversation exists and belongs to user
        conv_repo = ConversationRepository(db)
        conversation = conv_repo.get_by_id(conv_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Save user message to database
        message_repo.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        config = {
            "configurable": {
                "thread_id": conversation_id,
                "user_id": user_id
            }
        }
        inputs = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": user_id
        }
        
        # Broadcast thinking state
        await manager.broadcast({
            "type": "lumi_thinking",
            "conversation_id": conversation_id
        })

        full_content = ""
        # Use astream to capture tokens
        async for chunk, metadata in chat_agent.astream(inputs, config=config, stream_mode="messages"):
            if isinstance(chunk, AIMessage) and chunk.content:
                content_chunk = chunk.content
                if isinstance(content_chunk, list):
                    # Handle cases where content might be a list of dicts (e.g. tool calls)
                    # For a simple chat agent it's usually just a string
                    pass 
                else:
                    full_content += content_chunk
                    await manager.broadcast({
                        "type": "token",
                        "content": content_chunk,
                        "conversation_id": conversation_id
                    })
            elif hasattr(chunk, "tool_calls") and chunk.tool_calls:
                 # It's a message with tool calls, but maybe no content yet
                 pass
        
        # Broadcast done event
        await manager.broadcast({
            "type": "done",
            "conversation_id": conversation_id
        })

        # Save assistant response to database
        message_repo.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_content
        )
        
        return {
            "type": "chat_response",
            "content": full_content,
            "thread_id": conversation_id
        }
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
