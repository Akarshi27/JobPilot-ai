import os
import sys

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import SessionLocal, engine
from database.base import Base
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.profile import Profile
from backend.models.job import Job
from backend.services.job_scanner import scan_jobs
from backend.services.match_persistence import calculate_and_persist_match

# Initialize DB
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Create dummy user
user = db.query(User).filter(User.email == "test@example.com").first()
if not user:
    user = User(email="test@example.com", name="Test User", hashed_password="pw")
    db.add(user)
    db.commit()
    db.refresh(user)

# Ensure Profile exists with target role
profile = db.query(Profile).filter(Profile.user_id == user.id).first()
if not profile:
    profile = Profile(user_id=user.id, summary="Python developer looking for backend roles.", target_role="Python Backend Developer")
    db.add(profile)
    db.commit()
    db.refresh(profile)

# Add dummy resume
resume = db.query(Resume).filter(Resume.user_id == user.id).first()
if not resume:
    resume = Resume(
        user_id=user.id,
        original_filename="test.pdf",
        file_path="/tmp/test.pdf",
        file_type="application/pdf",
        extracted_text="I am a software engineer with 5 years of Python experience, specializing in FastAPI and Django.",
        analysis_status="COMPLETED_FALLBACK",
        is_current=True
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

# Run Job Scanner
print("Scanning jobs via Remotive...")
result = scan_jobs(db, user_id=user.id, limit=5)
print("Scan Result:", result)

# Verify Duplicate Prevention
print("Scanning again to verify duplicate prevention...")
result2 = scan_jobs(db, user_id=user.id, limit=5)
print("Scan Result 2 (should update, not add):", result2)

# Verify Job Records
jobs = db.query(Job).filter(Job.is_demo.is_(False)).all()
print(f"\nPersisted {len(jobs)} real jobs.")

valid_urls = 0
for job in jobs:
    if job.job_url:
        valid_urls += 1
    
print(f"Jobs with valid source_url: {valid_urls}")

# Test Matching and eligibility
print("\nTesting Matching Rankings:")
matches = []
for job in jobs:
    match = calculate_and_persist_match(db, user.id, job, force=True)
    matches.append(match)

# Sort by score descending
matches.sort(key=lambda m: m.match_score, reverse=True)

for m in matches:
    job = db.query(Job).filter(Job.id == m.job_id).first()
    eligibility = "ELIGIBLE (>=70%)" if m.match_score >= 70 else "RECOMMENDATION (<70%)"
    print(f"- {job.title} at {job.company}: {m.match_score:.1f}% -> {eligibility}")
    print(f"  URL: {job.job_url}")

db.close()
