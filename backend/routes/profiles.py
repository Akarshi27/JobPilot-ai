from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models.profile import Profile
from backend.models.user import User
from backend.schemas.profile import ProfileCreate, ProfileResponse
from database.database import get_db
from backend.utils.auth import get_current_user


router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"]
)


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/me", response_model=ProfileResponse)
def update_my_profile(data: ProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    for field, value in data.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post(
    "/{user_id}",
    response_model=ProfileResponse,
    status_code=201
)
def create_profile(
    user_id: int,
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own profile")
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    existing_profile = (
        db.query(Profile)
        .filter(Profile.user_id == user_id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists for this user."
        )

    profile = Profile(
        user_id=user_id,
        phone=profile_data.phone,
        location=profile_data.location,
        headline=profile_data.headline,
        summary=profile_data.summary,
        years_of_experience=profile_data.years_of_experience,
        target_role=profile_data.target_role
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.get(
    "/{user_id}",
    response_model=ProfileResponse
)
def get_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own profile")
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found."
        )

    return profile