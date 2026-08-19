import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.models.job import Job
from backend.schemas.job import JobCreate, JobResponse
from database.database import get_db
from backend.models.profile import Profile
from backend.models.resume import Resume
from backend.models.skill import Skill
from backend.models.job_skill import JobSkill
from backend.services.matching import semantic_match
from backend.utils.auth import get_current_user
from backend.services.match_persistence import calculate_and_persist_match
from backend.services.job_scanner import scan_jobs
from backend.models.job_skill import JobSkill


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.get("/recommendations")
def recommendations(
    limit: int = Query(default=20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_current.is_(True)).order_by(Resume.created_at.desc()).first()
    if not resume:
        return {"has_resume": False, "matches": []}
    if resume.analysis_status not in {"COMPLETED", "COMPLETED_FALLBACK"}:
        return {"has_resume": True, "analysis_status": resume.analysis_status, "matches": []}
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    skills = [skill.name for skill in db.query(Skill).filter(Skill.user_id == current_user.id).all()]
    candidate_text = "\n".join(filter(None, [resume.extracted_text if resume else "", profile.summary if profile else ""]))
    results = []
    for job in db.query(Job).filter(Job.is_active.is_(True)).order_by(Job.posted_at.desc().nullslast(), Job.created_at.desc()).limit(limit).all():
        match = calculate_and_persist_match(db, current_user.id, job)
        results.append({"id": job.id, "title": job.title, "company": job.company, "location": job.location, "source": job.source, "source_url": job.job_url, "is_demo": job.is_demo, "match_percentage": match.match_score, "matched_skills": match.matched_skills, "missing_skills": match.missing_required_skills, **(match.explanation or {})})
    db.commit()
    return sorted(results, key=lambda item: item["match_percentage"], reverse=True)


@router.post("/scan")
def scan_now(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_current.is_(True)).order_by(Resume.created_at.desc()).first()
    if not resume or resume.analysis_status not in {"COMPLETED", "COMPLETED_FALLBACK"}:
        raise HTTPException(status_code=409, detail="Complete resume analysis before scanning jobs")
    return scan_jobs(db, current_user.id)


@router.get("/diagnostic/provider")
def diagnostic_provider(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    import os
    import requests
    from backend.services.job_sources.public_api import PublicJobApiSource
    
    endpoint_url = os.getenv("PUBLIC_JOB_API_URL", "https://remotive.com/api/remote-jobs")
    provider_configured = bool(endpoint_url)
    
    provider_reachable = False
    jobs_retrieved = 0
    jobs_persisted = db.query(Job).filter(Job.is_demo.is_(False)).count()
    valid_source_url = db.query(Job).filter(Job.is_demo.is_(False), Job.job_url.isnot(None), Job.job_url != "").count()
    
    if provider_configured:
        try:
            source = PublicJobApiSource(endpoint=endpoint_url)
            # Test a small query to verify reachability
            results = source.search("python", limit=5)
            provider_reachable = True
            jobs_retrieved = len(results)
        except Exception as e:
            provider_reachable = False
            
    return {
        "provider_configured": provider_configured,
        "endpoint": endpoint_url,
        "provider_reachable": provider_reachable,
        "jobs_retrieved": jobs_retrieved,
        "jobs_persisted": jobs_persisted,
        "jobs_with_valid_source_url": valid_source_url
    }


@router.post("/seed-demo")
def seed_demo_jobs(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if os.getenv("ALLOW_DEMO_JOBS", "false").lower() != "true":
        raise HTTPException(status_code=403, detail="Demo jobs are disabled")
    demo_jobs = [
        ("Demo Python Backend Intern", "JobPilot Demo Lab", "Remote", "Build REST APIs and backend services using Python web frameworks.", ["Python", "REST APIs", "FastAPI"]),
        ("Demo Computer Vision Intern", "JobPilot Demo Lab", "Remote", "Work on image detection and deep learning projects for visual systems.", ["Computer Vision", "Deep Learning", "OpenCV"]),
        ("Demo Senior Java Engineer", "JobPilot Demo Lab", "Hybrid", "Lead enterprise services using Java and Spring Boot with five years of experience.", ["Java", "Spring Boot"]),
    ]
    created = 0
    for title, company, location, description, skills in demo_jobs:
        job = db.query(Job).filter(Job.title == title, Job.is_demo.is_(True)).first()
        if not job:
            job = Job(title=title, company=company, location=location, description=description, source="Demo", job_url=None, is_active=True, is_demo=True, requirements=skills)
            db.add(job)
            db.flush()
            for skill in skills:
                db.add(JobSkill(job_id=job.id, name=skill))
            created += 1
    db.commit()
    return {"status": "completed", "demo": True, "jobs_added": created, "jobs_available": db.query(Job).filter(Job.is_active.is_(True)).count(), "message": "Synthetic demo jobs are labeled Demo Job and cannot be applied to."}


@router.get("/search")
def search_jobs(
    query: str | None = None,
    location: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id, Resume.is_current.is_(True)).order_by(Resume.created_at.desc()).first()
    if not resume or resume.analysis_status not in {"COMPLETED", "COMPLETED_FALLBACK"}:
        raise HTTPException(status_code=409, detail="Complete resume analysis before searching jobs")
    jobs_query = db.query(Job)
    if query:
        jobs_query = jobs_query.filter(Job.title.ilike(f"%{query}%") | Job.description.ilike(f"%{query}%"))
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f"%{location}%"))
    return jobs_query.filter(Job.is_active.is_(True)).order_by(Job.created_at.desc()).limit(limit).all()


@router.post(
    "/",
    response_model=JobResponse,
    status_code=201
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db)
):
    job = Job(
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        description=job_data.description,
        source=job_data.source,
        job_url=job_data.job_url,
        is_active=True,
        is_demo=False,
        posted_at=job_data.posted_at
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
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

    if not job.is_active:
        raise HTTPException(status_code=404, detail="External job link unavailable")

    return job