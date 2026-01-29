from sqlalchemy.orm import Session
from src.common.models.users import User
from typing import Optional
import uuid

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_sub(self, sub: str) -> Optional[User]:
        return self.db.query(User).filter(User.sub == sub).first()

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_or_create_by_sub(self, sub: str) -> User:
        user = self.get_by_sub(sub)
        if not user:
            user = User(sub=sub)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user
