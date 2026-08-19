import hashlib
import re
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from backend.models.job import Job
from backend.models.job_skill import JobSkill
from backend.services.job_sources.base import NormalizedJob
from backend.services.skill_extractor import extract_skills


def canonical_url(url: str | None) -> str | None:
    if not url:
        return None
    return url.lower().strip().rstrip("/")


def is_real_source_url(url: str | None) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and parsed.hostname not in {"example.com", "localhost", "127.0.0.1"}


def job_fingerprint(job: NormalizedJob) -> str:
    value = f"{job.company}|{job.title}|{job.location or ''}|{re.sub(r'\W+', ' ', job.description.lower())}"
    return hashlib.sha256(value.encode()).hexdigest()


def upsert_job(db: Session, normalized: NormalizedJob) -> tuple[Job, bool]:
    if not is_real_source_url(normalized.url):
        raise ValueError("External job URL is required and must use HTTP or HTTPS")
    existing = db.query(Job).filter(Job.source == normalized.source, Job.external_id == normalized.external_id).first()
    if not existing and normalized.url:
        existing = db.query(Job).filter(Job.job_url == canonical_url(normalized.url)).first()
    if not existing:
        existing = db.query(Job).filter(Job.company == normalized.company, Job.title == normalized.title, Job.location == normalized.location).first()
    
    is_new = False
    if not existing:
        is_new = True
        existing = Job(source=normalized.source, external_id=normalized.external_id)
        db.add(existing)
    
    existing.title = normalized.title
    existing.company = normalized.company
    existing.location = normalized.location
    existing.remote = normalized.remote
    existing.description = normalized.description
    existing.requirements = normalized.requirements
    existing.preferred_skills = normalized.preferred_skills
    existing.salary_min = normalized.salary_min
    existing.salary_max = normalized.salary_max
    existing.employment_type = normalized.employment_type
    existing.experience_required = normalized.experience_required
    existing.job_url = canonical_url(normalized.url)
    existing.is_active = True
    existing.posted_at = normalized.posted_at
    db.flush()
    skills = dict.fromkeys(normalized.requirements + extract_skills(normalized.description))
    for skill in skills:
        if not db.query(JobSkill).filter(JobSkill.job_id == existing.id, JobSkill.name == skill).first():
            db.add(JobSkill(job_id=existing.id, name=skill))
    return existing, is_new