from sqlalchemy.orm import Session
from src.models.chat import Conversation, Message, ChatRun
from typing import List, Optional
import uuid

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str = "Untitled", user_id: Optional[str] = None) -> Conversation:
        db_conversation = Conversation(title=title, user_id=user_id)
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation

    def get_by_id(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def list_all(self, user_id: Optional[str] = None) -> List[Conversation]:
        query = self.db.query(Conversation)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        return query.order_by(Conversation.updated_at.desc()).all()

    def update_title(self, conversation_id: uuid.UUID, title: str) -> Optional[Conversation]:
        db_conversation = self.get_by_id(conversation_id)
        if db_conversation:
            db_conversation.title = title
            self.db.commit()
            self.db.refresh(db_conversation)
        return db_conversation

    def delete(self, conversation_id: uuid.UUID) -> bool:
        db_conversation = self.get_by_id(conversation_id)
        if db_conversation:
            self.db.delete(db_conversation)
            self.db.commit()
            return True
        return False

    def start_chat_run(self, user_id: str, thread_id: uuid.UUID) -> ChatRun:
        db_run = ChatRun(user_id=user_id, thread_id=thread_id, status="PROCESSING")
        self.db.add(db_run)
        self.db.commit()
        self.db.refresh(db_run)
        return db_run

    def end_chat_run(self, run_id: uuid.UUID, status: str = "COMPLETED") -> Optional[ChatRun]:
        db_run = self.db.query(ChatRun).filter(ChatRun.id == run_id).first()
        if db_run:
            db_run.status = status
            self.db.commit()
            self.db.refresh(db_run)
        return db_run

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_message(self, conversation_id: uuid.UUID, role: str, content: str) -> Message:
        db_message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_messages_by_conversation(self, conversation_id: uuid.UUID) -> List[Message]:
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
