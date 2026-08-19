from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.application import Application, ApplicationStatus
from backend.models.job import Job
from backend.models.job_match import JobMatch
from backend.models.user import User
from backend.services.application_providers import provider_for
from backend.utils.auth import get_current_user
from database.database import get_db


router = APIRouter(prefix="/applications", tags=["Applications"])


class ApplicationPatch(BaseModel):
    status: str | None = None
    notes: str | None = None


def _payload(application: Application) -> dict:
    return {
        "id": application.id,
        "job_id": application.job_id,
        "job_title": application.job.title,
        "company": application.job.company,
        "status": application.status,
        "match_score": application.match_score,
        "application_url": application.application_url,
        "source_url": application.application_url,
        "provider": application.provider,
        "automation_method": application.automation_method,
        "applied_at": application.applied_at,
        "last_updated_at": application.last_updated_at,
        "notes": application.notes,
    }


@router.get("")
def list_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.created_at.desc()).all()
    return [_payload(item) for item in applications]


@router.get("/{application_id}")
def get_application(application_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id, Application.user_id == current_user.id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return _payload(application)


@router.post("/{job_id}/approve")
def approve_application(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    match = db.query(JobMatch).filter(JobMatch.job_id == job_id, JobMatch.user_id == current_user.id).first()
    if not job or not match:
        raise HTTPException(status_code=404, detail="Job match not found")
    if match.match_score < 70:
        raise HTTPException(status_code=422, detail="Not eligible for application")
    application = db.query(Application).filter(Application.job_id == job_id, Application.user_id == current_user.id).first()
    if not application:
        application = Application(user_id=current_user.id, job_id=job_id, match_score=match.match_score, application_url=job.job_url, status=ApplicationStatus.APPROVED.value, provider=provider_for(job.job_url).name)
        db.add(application)
    else:
        application.status = ApplicationStatus.APPROVED.value
    db.commit()
    db.refresh(application)
    return _payload(application)

@router.post("/{job_id}/track")
def track_application(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    match = db.query(JobMatch).filter(JobMatch.job_id == job_id, JobMatch.user_id == current_user.id).first()
    if not job or not match:
        raise HTTPException(status_code=404, detail="Job match not found")
    application = db.query(Application).filter(Application.job_id == job_id, Application.user_id == current_user.id).first()
    if not application:
        application = Application(user_id=current_user.id, job_id=job_id, match_score=match.match_score, application_url=job.job_url, status=ApplicationStatus.APPLIED.value, applied_at=datetime.utcnow(), provider=provider_for(job.job_url).name)
        db.add(application)
    else:
        application.status = ApplicationStatus.APPLIED.value
        application.applied_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    return _payload(application)


@router.post("/{job_id}/apply")
def apply_application(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.job_id == job_id, Application.user_id == current_user.id).first()
    if not application or application.status not in {ApplicationStatus.APPROVED.value, ApplicationStatus.REVIEW_REQUIRED.value}:
        raise HTTPException(status_code=422, detail="Approve this eligible application before applying")
    provider = provider_for(application.application_url)
    result = provider.submit_application({"application_id": application.id, "url": application.application_url})
    application.status = ApplicationStatus.REVIEW_REQUIRED.value if result.status == "manual_required" else result.status
    application.notes = result.reason
    application.last_updated_at = datetime.utcnow()
    application.external_application_id = result.external_application_id
    db.commit()
    return {**_payload(application), "provider_result": result.status, "reason": result.reason}


@router.patch("/{application_id}")
def patch_application(application_id: int, data: ApplicationPatch, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id, Application.user_id == current_user.id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if data.status:
        application.status = data.status
    if data.notes is not None:
        application.notes = data.notes
    db.commit()
    db.refresh(application)
    return _payload(application)