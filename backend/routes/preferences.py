from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.user_preference import UserPreference
from backend.utils.auth import get_current_user
from database.database import get_db


router = APIRouter(prefix="/preferences", tags=["Preferences"])


class PreferenceUpdate(BaseModel):
    application_mode: str = Field(default="MANUAL", pattern="^(MANUAL|AUTO)$")
    minimum_match_threshold: int = Field(default=70, ge=0, le=100)
    preferred_location: str | None = None
    remote_preference: bool = False
    internship_preference: bool = False
    preferred_roles: list[str] = Field(default_factory=list)
    preferred_domains: list[str] = Field(default_factory=list)


@router.get("")
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preference = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not preference:
        preference = UserPreference(user_id=current_user.id)
        db.add(preference)
        db.commit()
        db.refresh(preference)
    return preference


@router.put("")
def update_preferences(data: PreferenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preference = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not preference:
        preference = UserPreference(user_id=current_user.id)
        db.add(preference)
    for key, value in data.model_dump().items():
        setattr(preference, key, value)
    db.commit()
    db.refresh(preference)
    return preference