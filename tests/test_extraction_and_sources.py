import pytest

from backend.schemas.extraction import ResumeExtraction
from backend.services.ai_service import _json_fragment
from backend.services.job_sources.base import normalize_job
from backend.services.job_sources.internshala import InternshalaJobSource
from backend.schemas.job import JobCreate


def test_malformed_fenced_json_is_recovered_and_validated():
    payload = _json_fragment('noise\n```json\n{"skills": ["FastAPI"], "projects": []}\n```')
    result = ResumeExtraction.model_validate(payload)
    assert result.skills == ["FastAPI"]
    assert result.projects == []


def test_job_normalization_cleans_whitespace():
    result = normalize_job({"id": 4, "title": " Backend   Intern ", "company": " ABC ", "description": " Build APIs  "}, "public_api")
    assert result.external_id == "4"
    assert result.title == "Backend Intern"
    assert result.company == "ABC"
    assert result.description == "Build APIs"


def test_restricted_provider_is_explicitly_unavailable():
    with pytest.raises(RuntimeError, match="unavailable"):
        InternshalaJobSource().search("backend intern")


def test_job_urls_require_http_or_https():
    valid = JobCreate(title="Backend Intern", company="Example", description="Build APIs", source="public_api", job_url="https://internshala.com/job/detail/backend-123")
    assert str(valid.job_url) == "https://internshala.com/job/detail/backend-123"
    with pytest.raises(ValueError):
        JobCreate(title="Backend Intern", company="Example", description="Build APIs", source="public_api", job_url="javascript:alert(1)")
    with pytest.raises(ValueError):
        JobCreate(title="Backend Intern", company="Example", description="Build APIs", source="public_api", job_url="https://example.com/jobs/fake")