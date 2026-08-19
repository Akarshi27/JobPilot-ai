from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.database import get_db
from backend.models.profile import Profile
from backend.models.skill import Skill
from backend.models.resume import Resume
from backend.models.user import User
from backend.utils.auth import get_current_user


router = APIRouter(
    prefix="/resume-analysis",
    tags=["Resume Analysis"]
)


class ResumeAnalysisRequest(BaseModel):
    resume_id: int
    user_id: int

    candidate_name: str | None = None
    email: str | None = None
    phone: str | None = None

    education: list = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list = Field(default_factory=list)
    work_experience: list = Field(default_factory=list)
    certifications: list = Field(default_factory=list)


@router.post("/save")
def save_resume_analysis(
    data: ResumeAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only analyze your own resume")

    # 1. Check resume
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == data.resume_id,
            Resume.user_id == data.user_id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    # 2. Find or create profile
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == data.user_id)
        .first()
    )

    if not profile:
        profile = Profile(
            user_id=data.user_id
        )
        db.add(profile)

    # Save phone if available
    if data.phone:
        profile.phone = data.phone

    # Make sure profile exists before continuing
    db.flush()

    # 3. Remove old resume-derived skills
    db.query(Skill).filter(
        Skill.user_id == data.user_id,
        Skill.source == "resume"
    ).delete(
        synchronize_session=False
    )

    # 4. Save newly extracted skills
    saved_skills = []

    for skill_name in data.skills:

        if not isinstance(skill_name, str):
            continue

        skill_name = skill_name.strip()

        if not skill_name:
            continue

        skill = Skill(
            user_id=data.user_id,
            name=skill_name,
            source="resume"
        )

        db.add(skill)
        saved_skills.append(skill_name)

    db.commit()

    return {
        "success": True,
        "resume_id": data.resume_id,
        "user_id": data.user_id,
        "skills_saved": saved_skills,
        "skills_count": len(saved_skills)
    }