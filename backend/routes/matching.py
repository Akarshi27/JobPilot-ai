from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.services.skill_gap import generate_skill_gap
from backend.models.job import Job
from backend.models.job_skill import JobSkill
from backend.models.skill import Skill
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.profile import Profile
from backend.services.matching import calculate_match, semantic_match
from backend.utils.auth import get_current_user
from database.database import get_db
from backend.services.match_persistence import calculate_and_persist_match


router = APIRouter(
    prefix="/matching",
    tags=["Matching"]
)


@router.get("/me/{job_id}")
def match_current_user_to_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_current.is_(True)).first()
    if not resume or resume.analysis_status not in {"COMPLETED", "COMPLETED_FALLBACK"}:
        return {"has_resume": False, "job_id": job.id, "matches": []}
    match = calculate_and_persist_match(db, current_user.id, job)
    db.commit()
    return {"job_id": job.id, "job_title": job.title, "company": job.company, "match_percentage": match.match_score, "matched_skills": match.matched_skills, "missing_skills": match.missing_required_skills, **(match.explanation or {})}


@router.get("/{user_id}/{job_id}")
def match_user_to_job(
    user_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only match your own profile")
    # Check user
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

    # Check job
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    # Get candidate skills
    candidate_skills = [
        skill.name
        for skill in db.query(Skill)
        .filter(Skill.user_id == user_id)
        .all()
    ]

    # Get job skills
    required_skills = [
        skill.name
        for skill in db.query(JobSkill)
        .filter(JobSkill.job_id == job_id)
        .all()
    ]

    result = calculate_match(
        candidate_skills,
        required_skills
    )

    skill_gap = generate_skill_gap(
    result["matched_skills"],
    result["missing_skills"]
    )

    return {
    "user_id": user_id,
    "job_id": job_id,
    "job_title": job.title,
    "company": job.company,
    **result,
    "skill_gap": skill_gap
    }