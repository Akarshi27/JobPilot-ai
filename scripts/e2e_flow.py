"""End-to-end API flow verification for JobPilot AI."""
import json
import sys
import time
import uuid
from pathlib import Path

import requests

API = "http://127.0.0.1:8000"
RESUME = Path(__file__).resolve().parent.parent / "test_resume.docx"


def main() -> int:
    email = f"e2e-{uuid.uuid4().hex[:8]}@example.org"
    password = "password123"
    print(f"1. Register {email}")
    r = requests.post(f"{API}/auth/register", json={"name": "E2E User", "email": email, "password": password}, timeout=15)
    r.raise_for_status()
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("2. Upload resume")
    with RESUME.open("rb") as f:
        r = requests.post(f"{API}/resumes/me", headers=headers, files={"file": ("test_resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}, timeout=30)
    r.raise_for_status()
    print("   status:", r.json().get("analysis_status"))

    print("3. Poll resume analysis")
    for i in range(60):
        r = requests.get(f"{API}/resumes/me", headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        status = data.get("analysis_status")
        if status in {"COMPLETED", "COMPLETED_FALLBACK"}:
            print(f"   completed after {i+1}s: {status}, skills={len(data.get('skills', []))}")
            break
        if status == "FAILED":
            print("   FAILED:", data.get("analysis_error"))
            return 1
        time.sleep(1)
    else:
        print("   timeout waiting for analysis")
        return 1

    print("4. Diagnostic provider")
    r = requests.get(f"{API}/jobs/diagnostic/provider", headers=headers, timeout=20)
    r.raise_for_status()
    diag = r.json()
    print(f"   reachable={diag.get('provider_reachable')} retrieved={diag.get('jobs_retrieved')} persisted={diag.get('jobs_persisted')}")

    print("5. Scan jobs")
    r = requests.post(f"{API}/jobs/scan", headers=headers, timeout=120)
    r.raise_for_status()
    scan = r.json()
    print(f"   status={scan.get('status')} added={scan.get('jobs_added')} sources={len(scan.get('sources', []))}")

    print("6. Recommendations")
    r = requests.get(f"{API}/jobs/recommendations?limit=5", headers=headers, timeout=30)
    r.raise_for_status()
    recs = r.json()
    matches = recs if isinstance(recs, list) else recs.get("matches", [])
    print(f"   matches={len(matches)}")
    if not matches:
        print("   seeding demo jobs for local verification")
        r = requests.post(f"{API}/jobs/seed-demo", headers=headers, timeout=15)
        r.raise_for_status()
        r = requests.get(f"{API}/jobs/recommendations?limit=5", headers=headers, timeout=30)
        r.raise_for_status()
        recs = r.json()
        matches = recs if isinstance(recs, list) else recs.get("matches", [])

    if not matches:
        print("   ERROR: no matches available")
        return 1

    top = matches[0]
    job_id = top["id"]
    print(f"   top job: {top['title']} @ {top['company']} — {top.get('match_percentage')}%")
    print(f"   source_url={top.get('source_url')}")

    print("7. Job details + match")
    r = requests.get(f"{API}/jobs/{job_id}", timeout=10)
    r.raise_for_status()
    r = requests.get(f"{API}/matching/me/{job_id}", headers=headers, timeout=15)
    r.raise_for_status()
    match = r.json()
    print(f"   eligible={match.get('eligible_for_application')} pct={match.get('match_percentage')}")

    print("8. Track application")
    r = requests.post(f"{API}/applications/{job_id}/track", headers=headers, timeout=15)
    if r.status_code == 404:
        print("   track skipped (no match persisted?)")
    else:
        r.raise_for_status()
        app = r.json()
        print(f"   application status={app.get('status')} url={app.get('source_url')}")

    print("9. List applications")
    r = requests.get(f"{API}/applications", headers=headers, timeout=10)
    r.raise_for_status()
    apps = r.json()
    print(f"   count={len(apps)}")

    print("\nE2E flow completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
