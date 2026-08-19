import os
import time

from backend.services.job_scanner import scan_jobs
from database.database import SessionLocal, create_database


def run() -> None:
    create_database()
    interval = max(1, int(os.getenv("JOB_SCAN_INTERVAL_MINUTES", "20"))) * 60
    while True:
        db = SessionLocal()
        try:
            result = scan_jobs(db)
            print(f"JobPilot scanner: {result['status']} ({result['matches_saved']} matches)", flush=True)
        finally:
            db.close()
        time.sleep(interval)


if __name__ == "__main__":
    run()