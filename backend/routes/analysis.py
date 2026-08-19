from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models.resume import Resume
from backend.models.skill import Skill
from backend.models.user import User
from backend.services.skill_extractor import extract_skills
from database.database import get_db
from backend.utils.auth import get_current_user


router = APIRouter(
    prefix="/analysis",
    tags=["Resume Analysis"]
)


@router.post("/{resume_id}/skills")
def analyze_resume_skills(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the resume
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    if not resume.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="Resume has no extracted text."
        )

    # Extract skills
    detected_skills = extract_skills(
        resume.extracted_text
    )

    # Get existing skills for this user
    existing_skills = {
        skill.name
        for skill in db.query(Skill)
        .filter(Skill.user_id == resume.user_id)
        .all()
    }

    # Add only new skills
    new_skills = []

    for skill_name in detected_skills:
        if skill_name not in existing_skills:
            skill = Skill(
                user_id=resume.user_id,
                name=skill_name,
                source="resume"
            )

            db.add(skill)
            new_skills.append(skill_name)

    db.commit()

    return {
        "resume_id": resume.id,
        "user_id": resume.user_id,
        "skills": detected_skills,
        "new_skills_added": new_skills,
        "skill_count": len(detected_skills)
    }