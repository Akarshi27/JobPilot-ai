import json
import os
import re
import requests

from backend.schemas.extraction import ResumeExtraction
from backend.services.ai_providers.base import BaseAIProvider


class OllamaProvider(BaseAIProvider):
    def __init__(self):
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen3:4b")
        self.embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
        self._available = True

    @property
    def provider_name(self) -> str:
        return "ollama"

    def is_available(self) -> bool:
        return self._available

    def _json_fragment(self, value: str) -> dict:
        cleaned = value.strip()
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("Ollama did not return a JSON object")
        return json.loads(cleaned[start:end + 1])

    def _prompt(self, resume_text: str) -> str:
        return f"""Extract a resume into JSON. Use ONLY facts explicitly present in the resume.
Never infer or guess technologies, employers, degrees, dates, certifications, or contact details.
The skills array must contain only flat skill names explicitly mentioned in the text.
A project is included only when the resume identifies it as a project. Work experience is only actual employment or internships.
Return JSON only, with exactly these keys: candidate_name, email, phone, location, summary, education, skills, projects, work_experience, certifications.
For projects use objects with name, description, technologies. For education use institution, degree, field, dates.
For work_experience use company, title, description, dates. Do not add commentary.

RESUME TEXT:
{resume_text[:30000]}"""

    def extract_resume(self, resume_text: str) -> ResumeExtraction:
        if not resume_text.strip():
            raise ValueError("Resume text is empty")
        
        last_error: Exception | None = None
        for attempt in range(2):
            if not self._available:
                raise RuntimeError("Ollama service is unavailable")
            try:
                response = requests.post(
                    f"{self.url}/api/generate",
                    json={"model": self.model, "prompt": self._prompt(resume_text), "stream": False, "format": "json"},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                raw = response.json().get("response", "")
                return ResumeExtraction.model_validate(self._json_fragment(raw))
            except requests.exceptions.ConnectionError as exc:
                self._available = False
                raise RuntimeError(f"Ollama connection failed: {exc}") from exc
            except (requests.RequestException, ValueError, TypeError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt == 0:
                    continue
        raise RuntimeError(f"Resume AI extraction unavailable or invalid: {last_error}") from last_error

    def embed_text(self, text: str) -> list[float]:
        if not self._available:
            raise RuntimeError("Ollama service is unavailable")
            
        try:
            response = requests.post(
                f"{self.url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=5,
            )
            response.raise_for_status()
            embedding = response.json().get("embedding")
            if embedding:
                return embedding
        except requests.exceptions.ConnectionError as exc:
            self._available = False
            raise RuntimeError(f"Ollama connection failed: {exc}") from exc
        except (requests.RequestException, ValueError, TypeError) as exc:
            raise RuntimeError(f"Ollama embedding failed: {exc}") from exc
            
        raise RuntimeError("Ollama returned empty embedding")
