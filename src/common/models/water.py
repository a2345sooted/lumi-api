from sqlalchemy import Column, String, DateTime, func, Numeric
from sqlalchemy.dialects.postgresql import UUID
from src.common.database import Base
import uuid

class UserWaterLog(Base):
    __tablename__ = "user_water_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    amount_oz = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
