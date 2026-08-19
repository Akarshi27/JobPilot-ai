import threading

from sqlalchemy.orm import Session

from backend.models.job import Job
from backend.models.user import User
from backend.models.application import Application, ApplicationStatus
from backend.models.user_preference import UserPreference
from backend.services.job_ingestion import upsert_job
from backend.services.job_sources import CompanyCareerSource, InternshalaJobSource, PublicJobApiSource
from backend.services.match_persistence import calculate_and_persist_match


scan_lock = threading.Lock()


def scan_jobs(db: Session, user_id: int | None = None, limit: int = 25) -> dict:
    if not scan_lock.acquire(blocking=False):
        return {"status": "already_running", "jobs_added": 0, "matches_saved": 0, "sources": []}
    try:
        users = [db.query(User).filter(User.id == user_id).first()] if user_id else db.query(User).all()
        users = [user for user in users if user]
        queries = []
        for user in users:
            profile = user.profile
            queries.append(" ".join(filter(None, [profile.target_role if profile else "", profile.headline if profile else "", *(item.name for item in user.skills)])) or "software engineering")
        query = queries[0] if queries else "software engineering"
        sources = [PublicJobApiSource(), InternshalaJobSource(), CompanyCareerSource()]
        jobs_added = 0
        jobs_updated = 0
        touched_job_ids: set[int] = set()
        source_status = []
        errors = []
        sources_checked = []
        for source in sources:
            sources_checked.append(source.name)
            try:
                records = source.search(query, limit=limit)
                for record in records:
                    try:
                        job, is_new = upsert_job(db, record)
                        touched_job_ids.add(job.id)
                        if is_new:
                            jobs_added += 1
                        else:
                            jobs_updated += 1
                    except ValueError:
                        # Skip invalid URLs
                        continue
                source_status.append({"source": source.name, "status": "ok", "count": len(records)})
            except Exception as exc:
                errors.append(f"{source.name}: {exc}")
                source_status.append({"source": source.name, "status": "unavailable", "reason": str(exc)})
        db.commit()
        matches_saved = 0
        for user in users:
            for job_id in touched_job_ids:
                job = db.query(Job).filter(Job.id == job_id, Job.is_active.is_(True)).first()
                if not job:
                    continue
                match = calculate_and_persist_match(db, user.id, job, force=True)
                preference = db.query(UserPreference).filter(UserPreference.user_id == user.id).first()
                if preference and preference.application_mode == "AUTO" and match.match_score >= preference.minimum_match_threshold:
                    existing_application = db.query(Application).filter(Application.user_id == user.id, Application.job_id == job.id).first()
                    if existing_application is None:
                        db.add(Application(user_id=user.id, job_id=job.id, match_score=match.match_score, application_url=job.job_url, status=ApplicationStatus.ELIGIBLE.value, automation_method="AUTO", provider="manual"))
                matches_saved += 1
        db.commit()
        return {
            "status": "completed",
            "success": True,
            "sources": source_status,
            "sources_checked": sources_checked,
            "jobs_found": sum(item.get("count", 0) for item in source_status if item.get("status") == "ok"),
            "jobs_added": jobs_added,
            "jobs_updated": jobs_updated,
            "matches_saved": matches_saved,
            "errors": errors,
        }
    finally:
        scan_lock.release()