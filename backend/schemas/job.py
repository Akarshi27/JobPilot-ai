from datetime import datetime

from pydantic import BaseModel
from pydantic import HttpUrl, field_validator
from urllib.parse import urlparse


class JobCreate(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str
    source: str
    job_url: HttpUrl
    posted_at: datetime | None = None

    @field_validator("job_url")
    @classmethod
    def normalize_job_url(cls, value: HttpUrl) -> str:
        url = str(value).rstrip("/")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.hostname in {"example.com", "localhost", "127.0.0.1"}:
            raise ValueError("Job URL must use HTTP or HTTPS")
        return url


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str | None
    description: str
    source: str
    job_url: str | None
    source_url: str | None = None
    url: str | None = None
    posted_at: datetime | None
    created_at: datetime
    external_id: str | None = None
    remote: bool = False
    requirements: list = []
    preferred_skills: list = []
    salary_min: float | None = None
    salary_max: float | None = None
    employment_type: str | None = None
    experience_required: str | None = None
    is_active: bool = True
    is_demo: bool = False

    class Config:
        from_attributes = True