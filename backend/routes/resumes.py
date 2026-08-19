from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from backend.services.n8n_service import trigger_resume_processing
from backend.utils.auth import get_current_user
from backend.models.resume import Resume
from backend.models.user import User
from backend.models.skill import Skill
from backend.models.profile import Profile
from backend.models.job_match import JobMatch
from backend.schemas.resume import ResumeResponse
from backend.services.resume_parser import extract_resume_text
from backend.services.ai_service import extract_resume
from backend.services.skill_extractor import extract_skills
from backend.schemas.extraction import ResumeExtraction
from database.database import SessionLocal, get_db


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


def current_resume_query(db: Session, user_id: int):
    return db.query(Resume).filter(Resume.user_id == user_id, Resume.is_current.is_(True)).order_by(Resume.created_at.desc())


def resume_payload(resume: Resume | None, db: Session, user_id: int) -> dict:
    if not resume:
        return {"has_resume": False, "resume": None}
    extracted = resume.extraction_data or {}
    return {
        "has_resume": True,
        "id": resume.id,
        "original_filename": resume.original_filename,
        "file_type": resume.file_type,
        "created_at": resume.created_at,
        "analysis_status": resume.analysis_status,
        "analysis_error": resume.analysis_error,
        "is_current": resume.is_current,
        "skills": [skill.name for skill in db.query(Skill).filter(Skill.user_id == user_id, Skill.source == "resume").all()],
        "education": extracted.get("education", []),
        "projects": extracted.get("projects", []),
        "work_experience": extracted.get("work_experience", []),
        "certifications": extracted.get("certifications", []),
    }


@router.get("/me")
def current_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return resume_payload(current_resume_query(db, current_user.id).first(), db, current_user.id)


@router.delete("/me")
def delete_current_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = current_resume_query(db, current_user.id).first()
    if resume:
        resume.is_current = False
        db.query(Skill).filter(Skill.user_id == current_user.id, Skill.source == "resume").delete(synchronize_session=False)
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if profile:
            profile.summary = None
            profile.education = []
            profile.projects = []
            profile.work_experience = []
            profile.certifications = []
        db.query(JobMatch).filter(JobMatch.user_id == current_user.id).delete(synchronize_session=False)
        db.commit()
    return {"has_resume": False}


@router.get("/me/status")
def resume_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = current_resume_query(db, current_user.id).first()
    if not resume:
        return {"state": "NO_RESUME", "has_resume": False, "has_completed_analysis": False, "analysis_status": None}
    completed = resume.analysis_status in {"COMPLETED", "COMPLETED_FALLBACK"}
    state = "ANALYSIS_FALLBACK" if resume.analysis_status == "COMPLETED_FALLBACK" else (
        "ANALYSIS_COMPLETED" if completed else ("ANALYZING" if resume.analysis_status in {"PROCESSING", "PENDING"} else "ANALYSIS_FAILED")
    )
    return {
        "state": state,
        "has_resume": True,
        "has_completed_analysis": completed,
        "analysis_status": resume.analysis_status,
        "analysis_error": resume.analysis_error,
        "resume_id": resume.id,
    }


@router.get("/me/latest")
def latest_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = current_resume_query(db, current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded")
    extracted = resume.extraction_data or {}
    return {
        "id": resume.id,
        "filename": resume.original_filename,
        "analysis_status": resume.analysis_status,
        "analysis_error": resume.analysis_error,
        "skills": [skill.name for skill in db.query(Skill).filter(Skill.user_id == current_user.id, Skill.source == "resume").all()],
        "education": extracted.get("education", []),
        "projects": extracted.get("projects", []),
        "work_experience": extracted.get("work_experience", []),
        "certifications": extracted.get("certifications", []),
    }


@router.post("/me", status_code=201)
async def upload_my_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await upload_resume(current_user.id, file=file, current_user=current_user, background_tasks=background_tasks, db=db)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def process_resume_analysis(resume_id: int, user_id: int) -> None:
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        user = db.query(User).filter(User.id == user_id).first()
        if not resume or not user or not resume.extracted_text:
            return
        try:
            extracted = extract_resume(resume.extracted_text)
            resume.extraction_data = extracted.model_dump()
            resume.analysis_status = "COMPLETED"
            resume.analysis_error = None
            profile = user.profile
            if profile is None:
                from backend.models.profile import Profile
                profile = Profile(user_id=user_id)
                db.add(profile)
            profile.phone = extracted.phone or profile.phone
            profile.location = extracted.location or profile.location
            profile.summary = extracted.summary or profile.summary
            profile.education = [item.model_dump() for item in extracted.education]
            profile.projects = [item.model_dump() for item in extracted.projects]
            profile.work_experience = [item.model_dump() for item in extracted.work_experience]
            profile.certifications = extracted.certifications
            db.query(Skill).filter(Skill.user_id == user_id, Skill.source == "resume").delete(synchronize_session=False)
            for skill_name in dict.fromkeys(extracted.skills):
                skill_name = skill_name.strip()
                if skill_name:
                    db.add(Skill(user_id=user_id, name=skill_name, source="resume"))
        except (RuntimeError, ValueError) as exc:
            fallback = ResumeExtraction(skills=extract_skills(resume.extracted_text))
            resume.extraction_data = fallback.model_dump()
            resume.analysis_status = "COMPLETED_FALLBACK"
            resume.analysis_error = f"AI extraction unavailable; evidence-only skill fallback used: {exc}"[:500]
            db.query(Skill).filter(Skill.user_id == user_id, Skill.source == "resume").delete(synchronize_session=False)
            for skill_name in dict.fromkeys(fallback.skills):
                db.add(Skill(user_id=user_id, name=skill_name, source="resume"))
        db.commit()
        trigger_resume_processing(resume_id=resume.id, user_id=user_id, resume_text=resume.extracted_text)
    finally:
        db.close()


@router.post(
    "/{user_id}",
    status_code=201
)
async def upload_resume(
    user_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only upload your own resume")
    # Check whether the user exists
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

    # Check file extension
    original_filename = file.filename or ""
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX resumes are supported."
        )

    # Generate a unique stored filename
    stored_filename = f"{uuid4().hex}{extension}"
    stored_path = UPLOAD_DIR / stored_filename

    # Save uploaded file
    file_contents = await file.read()
    if len(file_contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Resume must be smaller than 10 MB")
    stored_path.write_bytes(file_contents)

    # Extract resume text
    try:
        extracted_text = extract_resume_text(
            str(stored_path),
            file.content_type or ""
        )
    except Exception as exc:
        stored_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=f"Could not extract resume text: {exc}"
        )

    # Make sure the resume actually contains text
    if not extracted_text.strip():
        stored_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Could not extract readable text from the resume."
        )

    # Store resume information in database
    db.query(Resume).filter(Resume.user_id == user_id, Resume.is_current.is_(True)).update({"is_current": False}, synchronize_session=False)
    db.query(Skill).filter(Skill.user_id == user_id, Skill.source == "resume").delete(synchronize_session=False)
    db.query(JobMatch).filter(JobMatch.user_id == user_id).delete(synchronize_session=False)
    resume = Resume(
        user_id=user_id,
        original_filename=original_filename,
        file_path=str(stored_path),
        file_type=file.content_type or extension,
        extracted_text=extracted_text,
        analysis_status="PROCESSING",
        is_current=True,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    background_tasks.add_task(process_resume_analysis, resume.id, user_id)

    return resume_payload(resume, db, user_id)