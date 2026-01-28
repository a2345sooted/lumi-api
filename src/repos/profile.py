from sqlalchemy.orm import Session
from src.models.profile import UserProfile
from typing import Any, Dict, Optional
import uuid

class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: Optional[str] = None) -> Optional[UserProfile]:
        query = self.db.query(UserProfile)
        if user_id:
            query = query.filter(UserProfile.user_id == user_id)
        return query.first()

    def update_profile(self, profile_data: Dict[str, Any], user_id: Optional[str] = None) -> UserProfile:
        db_profile = self.get_profile(user_id=user_id)
        if not db_profile:
            db_profile = UserProfile(profile_info=profile_data, user_id=user_id)
            self.db.add(db_profile)
        else:
            # Merge new data into existing JSONB
            current_info = dict(db_profile.profile_info)
            current_info.update(profile_data)
            db_profile.profile_info = current_info
        
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile
