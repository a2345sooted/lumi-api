from sqlalchemy.orm import Session
from src.common.models.water import UserWaterLog
from typing import List, Optional
import uuid

class WaterRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: uuid.UUID, amount_oz: float) -> UserWaterLog:
        db_log = UserWaterLog(user_id=user_id, amount_oz=amount_oz)
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log

    def get_by_id(self, log_id: uuid.UUID) -> Optional[UserWaterLog]:
        return self.db.query(UserWaterLog).filter(UserWaterLog.id == log_id).first()

    def list_all(self, user_id: uuid.UUID) -> List[UserWaterLog]:
        return self.db.query(UserWaterLog).filter(UserWaterLog.user_id == user_id).order_by(UserWaterLog.created_at.desc()).all()

    def delete(self, log_id: uuid.UUID) -> bool:
        db_log = self.get_by_id(log_id)
        if db_log:
            self.db.delete(db_log)
            self.db.commit()
            return True
        return False
