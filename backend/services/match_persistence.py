from sqlalchemy.orm import Session

from backend.models.job import Job
from backend.models.job_match import JobMatch
from backend.models.profile import Profile
from backend.models.resume import Resume
from backend.models.skill import Skill
from backend.services.matching import semantic_match


def calculate_and_persist_match(db: Session, user_id: int, job: Job, force: bool = False) -> JobMatch:
    existing = db.query(JobMatch).filter(JobMatch.user_id == user_id, JobMatch.job_id == job.id).first()
    if existing and not force:
        return existing
    resume = db.query(Resume).filter(Resume.user_id == user_id, Resume.is_current.is_(True)).order_by(Resume.created_at.desc()).first()
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    skills = [item.name for item in db.query(Skill).filter(Skill.user_id == user_id).all()]
    candidate_text = "\n".join(filter(None, [resume.extracted_text if resume else "", profile.summary if profile else "", str(profile.projects if profile else "")]))
    requirements = list(job.requirements or [])
    if not requirements:
        requirements = [item.name for item in job.skills]
    result = semantic_match(
        candidate_text or "No resume uploaded",
        "\n".join(filter(None, [job.title, job.description, str(requirements), str(job.preferred_skills or [])])),
        skills,
        requirements,
        str(profile.years_of_experience if profile else 0),
        str(profile.education if profile else ""),
    )
    preferred = [skill for skill in (job.preferred_skills or []) if skill not in result["matched_skills"]]
    if existing is None:
        existing = JobMatch(user_id=user_id, job_id=job.id)
        db.add(existing)
    existing.match_score = result["match_percentage"]
    existing.semantic_score = result["semantic_score"]
    existing.skill_score = result["skill_score"]
    existing.project_score = result["project_score"]
    existing.experience_score = result["experience_score"]
    existing.education_score = result["education_score"]
    existing.matched_skills = result["matched_skills"]
    existing.missing_required_skills = result["missing_skills"]
    existing.missing_preferred_skills = preferred
    existing.explanation = result
    db.flush()
    return existing