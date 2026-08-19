from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass
class NormalizedJob:
    external_id: str
    source: str
    title: str
    company: str
    location: str | None
    remote: bool
    description: str
    requirements: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    salary_min: float | None = None
    salary_max: float | None = None
    employment_type: str | None = None
    experience_required: str | None = None
    url: str | None = None
    posted_at: datetime | None = None


class JobSource(Protocol):
    name: str
    def search(self, query: str, location: str | None = None, limit: int = 25) -> list[NormalizedJob]: ...
    def fetch_job(self, external_id: str) -> NormalizedJob | None: ...


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").split()).strip()


def normalize_job(raw: dict, source: str) -> NormalizedJob:
    title = normalize_text(raw.get("title")) or "Untitled role"
    company = normalize_text(raw.get("company") or raw.get("company_name")) or "Unknown company"
    description = normalize_text(raw.get("description") or raw.get("job_description"))
    return NormalizedJob(
        external_id=str(raw.get("external_id") or raw.get("id") or raw.get("url") or f"{company}:{title}"),
        source=source,
        title=title,
        company=company,
        location=normalize_text(raw.get("location")) or None,
        remote=bool(raw.get("remote", False)),
        description=description,
        requirements=[normalize_text(item) for item in raw.get("requirements", []) if normalize_text(item)],
        preferred_skills=[normalize_text(item) for item in raw.get("preferred_skills", []) if normalize_text(item)],
        salary_min=raw.get("salary_min"),
        salary_max=raw.get("salary_max"),
        employment_type=normalize_text(raw.get("employment_type")) or None,
        experience_required=normalize_text(raw.get("experience_required")) or None,
        url=normalize_text(raw.get("url") or raw.get("job_url")) or None,
        posted_at=raw.get("posted_at"),
    )