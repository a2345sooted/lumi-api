from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import uuid
import datetime
import logging
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from src.agents.registry import get_chat_agent
from src.database import get_db
from src.repos.chat import ConversationRepository, MessageRepository

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
async def create_conversation(db: Session = Depends(get_db)):
    repo = ConversationRepository(db)
    conversation = repo.create()
    return {"id": str(conversation.id)}

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(db: Session = Depends(get_db)):
    repo = ConversationRepository(db)
    conversations = repo.list_all()
    return conversations

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    repo = MessageRepository(db)
    try:
        conv_id = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    
    messages = repo.get_messages_by_conversation(conv_id)
    return messages

@router.post("/conversations/{conversation_id}/messages")
async def post_user_message(
    conversation_id: str, 
    request: UserMessageRequest,
    db: Session = Depends(get_db)
):
    chat_agent = get_chat_agent()
    message_repo = MessageRepository(db)
    
    try:
        # Save user message to database
        message_repo.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        config = {"configurable": {"thread_id": conversation_id}}
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        result = await chat_agent.ainvoke(inputs, config=config)
        
        final_message = result["messages"][-1]
        
        # Save assistant response to database
        message_repo.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=final_message.content
        )
        
        return {
            "type": "chat_response",
            "content": final_message.content,
            "thread_id": conversation_id
        }
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
