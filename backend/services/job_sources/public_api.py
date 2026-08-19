import os
from datetime import datetime
import requests

from backend.services.job_sources.base import NormalizedJob, normalize_job


class PublicJobApiSource:
    name = "remotive"

    def __init__(self, endpoint: str | None = None):
        # We default to Remotive API which requires no auth.
        self.endpoint = endpoint or os.getenv("PUBLIC_JOB_API_URL", "https://remotive.com/api/remote-jobs")

    def search(self, query: str, location: str | None = None, limit: int = 25) -> list[NormalizedJob]:
        if not self.endpoint:
            raise RuntimeError("No external job source configured")
        
        # Remotive supports search and limit. Location is generally worldwide for remote jobs.
        params = {"search": query, "limit": limit}
        response = requests.get(self.endpoint, params=params, timeout=10)
        response.raise_for_status()
        
        payload = response.json()
        records = payload if isinstance(payload, list) else payload.get("jobs", [])
        
        normalized_jobs = []
        for record in records:
            if not isinstance(record, dict):
                continue
            
            # Map Remotive specific fields to our internal format
            mapped_record = dict(record)
            if "tags" in record and isinstance(record["tags"], list):
                mapped_record["requirements"] = record["tags"]
            if "candidate_required_location" in record:
                mapped_record["location"] = record["candidate_required_location"]
            if "publication_date" in record:
                try:
                    mapped_record["posted_at"] = datetime.fromisoformat(record["publication_date"])
                except ValueError:
                    pass
            if "job_type" in record:
                mapped_record["employment_type"] = record["job_type"]
                
            normalized_jobs.append(normalize_job(mapped_record, self.name))
        
        # Enforce limit as Remotive sometimes ignores it
        return normalized_jobs[:limit]

    def fetch_job(self, external_id: str) -> NormalizedJob | None:
        return None