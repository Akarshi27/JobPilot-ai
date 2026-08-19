from backend.schemas.extraction import ResumeExtraction
from backend.services.ai_providers import get_ai_provider
import json
import re


def _json_fragment(value: str) -> dict:
    cleaned = value.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Ollama did not return a JSON object")
    return json.loads(cleaned[start:end + 1])


def extract_resume(resume_text: str) -> ResumeExtraction:
    """Extract structured data from resume text using the configured AI provider."""
    provider = get_ai_provider()
    return provider.extract_resume(resume_text)