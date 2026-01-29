from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uuid
import datetime
from sqlalchemy.orm import Session
from src.common.database import get_db
from src.common.repos.water import WaterRepository
from src.api_server.api.auth import get_current_user_id

router = APIRouter()

class WaterLogCreate(BaseModel):
    amount_oz: float
    drank_at: Optional[datetime.datetime] = None

class WaterLogResponse(BaseModel):
    id: uuid.UUID
    amount_oz: float
    drank_at: datetime.datetime
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=List[WaterLogResponse])
async def list_water_logs(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repo = WaterRepository(db)
    return repo.list_all(user_id=user_id)

@router.post("/", response_model=WaterLogResponse)
async def create_water_log(
    request: WaterLogCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repo = WaterRepository(db)
    return repo.create(
        user_id=user_id, 
        amount_oz=request.amount_oz,
        drank_at=request.drank_at
    )

@router.delete("/{log_id}")
async def delete_water_log(
    log_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repo = WaterRepository(db)
    log = repo.get_by_id(log_id)
    if not log or log.user_id != user_id:
        raise HTTPException(status_code=404, detail="Water log not found")
    
    success = repo.delete(log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Water log not found")
    
    return {"status": "success", "message": "Water log deleted"}
