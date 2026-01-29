from sqlalchemy.orm import Session
from src.common.models.chat import UserMessage, ChatRun
from typing import List, Optional
import uuid

class UserMessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_message(self, user_id: uuid.UUID, role: str, content: str) -> UserMessage:
        db_message = UserMessage(
            user_id=user_id,
            role=role,
            content=content
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_messages_by_user(self, user_id: uuid.UUID) -> List[UserMessage]:
        return self.db.query(UserMessage).filter(UserMessage.user_id == user_id).order_by(UserMessage.created_at.asc()).all()

    def start_chat_run(self, user_id: uuid.UUID, thread_id: uuid.UUID) -> ChatRun:
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
