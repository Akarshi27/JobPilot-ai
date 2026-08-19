from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models.job import Job
from backend.models.job_skill import JobSkill
from backend.services.job_skill_extractor import extract_job_skills
from database.database import get_db


router = APIRouter(
    prefix="/job-analysis",
    tags=["Job Analysis"]
)


@router.post("/{job_id}/skills")
def analyze_job_skills(
    job_id: int,
    db: Session = Depends(get_db)
):
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

    detected_skills = extract_job_skills(
        job.description
    )

    existing_skills = {
        skill.name
        for skill in db.query(JobSkill)
        .filter(JobSkill.job_id == job.id)
        .all()
    }

    new_skills = []

    for skill_name in detected_skills:
        if skill_name not in existing_skills:
            job_skill = JobSkill(
                job_id=job.id,
                name=skill_name
            )

            db.add(job_skill)
            new_skills.append(skill_name)

    db.commit()

    return {
        "job_id": job.id,
        "title": job.title,
        "company": job.company,
        "required_skills": detected_skills,
        "new_skills_added": new_skills,
        "skill_count": len(detected_skills)
    }