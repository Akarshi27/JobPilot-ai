import json
import os
import re

import requests

from backend.schemas.extraction import ResumeExtraction


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b-instruct")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "15"))
_ollama_available = True


def _json_fragment(value: str) -> dict:
    cleaned = value.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Ollama did not return a JSON object")
    return json.loads(cleaned[start:end + 1])


def _prompt(resume_text: str) -> str:
    return f"""Extract a resume into JSON. Use ONLY facts explicitly present in the resume.
Never infer or guess technologies, employers, degrees, dates, certifications, or contact details.
The skills array must contain only flat skill names explicitly mentioned in the text.
A project is included only when the resume identifies it as a project. Work experience is only actual employment or internships.
Return JSON only, with exactly these keys: candidate_name, email, phone, location, summary, education, skills, projects, work_experience, certifications.
For projects use objects with name, description, technologies. For education use institution, degree, field, dates.
For work_experience use company, title, description, dates. Do not add commentary.

RESUME TEXT:
{resume_text[:30000]}"""


def extract_resume(resume_text: str) -> ResumeExtraction:
    global _ollama_available
    if not resume_text.strip():
        raise ValueError("Resume text is empty")
    last_error: Exception | None = None
    for attempt in range(2):
        if not _ollama_available:
            raise RuntimeError("Ollama service is unavailable")
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": _prompt(resume_text), "stream": False, "format": "json"},
                timeout=OLLAMA_TIMEOUT,
            )
            response.raise_for_status()
            raw = response.json().get("response", "")
            return ResumeExtraction.model_validate(_json_fragment(raw))
        except requests.exceptions.ConnectionError as exc:
            _ollama_available = False
            raise RuntimeError(f"Ollama connection failed: {exc}") from exc
        except (requests.RequestException, ValueError, TypeError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == 0:
                continue
    raise RuntimeError(f"Resume AI extraction unavailable or invalid: {last_error}") from last_error