from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.common.database import get_db
from src.api_server.api.auth import get_current_user_id
from src.common.repos.users import UserRepository
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/me")
async def get_user_info(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # The user is already created/resolved in get_current_user_id
    return {}
