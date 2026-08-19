from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import JobMatch, Profile, Resume, Skill, User
from backend.services.job_ingestion import upsert_job
from backend.services.job_sources.base import NormalizedJob
from backend.utils.security import hash_password
from database.base import Base


def test_current_resume_replacement_invalidates_derived_state():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    user = User(name="Lifecycle User", email="lifecycle@test.local", password_hash=hash_password("password"))
    session.add(user)
    session.flush()
    first = Resume(user_id=user.id, original_filename="first.pdf", file_path="uploads/first.pdf", file_type="application/pdf", extracted_text="Python", is_current=True, analysis_status="COMPLETED")
    session.add(first)
    session.add(Skill(user_id=user.id, name="Python", source="resume"))
    session.add(Profile(user_id=user.id, summary="First profile"))
    session.flush()
    job, _ = upsert_job(session, NormalizedJob(external_id="1", source="api", title="Role", company="Co", location="Remote", remote=True, description="Build APIs", url="https://internshala.com/job/detail/role-1"))
    session.add(JobMatch(user_id=user.id, job_id=job.id, match_score=80))
    session.query(Resume).filter(Resume.user_id == user.id, Resume.is_current.is_(True)).update({"is_current": False})
    second = Resume(user_id=user.id, original_filename="second.pdf", file_path="uploads/second.pdf", file_type="application/pdf", extracted_text="Java", is_current=True, analysis_status="PROCESSING")
    session.add(second)
    session.query(Skill).filter(Skill.user_id == user.id, Skill.source == "resume").delete(synchronize_session=False)
    session.query(JobMatch).filter(JobMatch.user_id == user.id).delete(synchronize_session=False)
    session.commit()
    assert session.query(Resume).filter(Resume.user_id == user.id, Resume.is_current.is_(True)).one().original_filename == "second.pdf"
    assert session.query(Skill).filter_by(user_id=user.id, source="resume").count() == 0
    assert session.query(JobMatch).filter_by(user_id=user.id).count() == 0