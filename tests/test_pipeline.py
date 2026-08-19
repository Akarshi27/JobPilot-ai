from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Application, Job, Profile, User
from backend.models.job_match import JobMatch
from backend.services.application_providers import ManualApplicationProvider
from backend.services.job_ingestion import upsert_job
from backend.services.job_sources.base import NormalizedJob
from backend.services.match_persistence import calculate_and_persist_match
from backend.utils.security import hash_password
from database.base import Base


def test_ingest_match_and_manual_application_pipeline(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    monkeypatch.setattr("backend.services.matching.embed_text", lambda text: [1.0, 0.0] if "backend" in text.lower() or "api" in text.lower() else [0.8, 0.6])
    user = User(name="Pipeline User", email="pipeline@test.local", password_hash=hash_password("password"))
    session.add(user)
    session.flush()
    session.add(Profile(user_id=user.id, summary="Built backend API projects", projects=[{"name": "API project"}]))
    job, _ = upsert_job(session, NormalizedJob(external_id="job-1", source="public_api", title="Backend Intern", company="Example", location="Remote", remote=True, description="Build backend APIs", requirements=["Python web frameworks"], url="https://internshala.com/job/detail/backend-1"))
    session.commit()
    match = calculate_and_persist_match(session, user.id, job, force=True)
    session.commit()
    assert session.query(JobMatch).filter_by(user_id=user.id, job_id=job.id).one().match_score >= 70
    assert match.missing_required_skills == []
    result = ManualApplicationProvider().submit_application({"url": job.job_url})
    assert result.status == "manual_required"
    assert session.query(Application).count() == 0