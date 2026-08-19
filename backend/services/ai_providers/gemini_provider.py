import os
from typing import List

from google import genai
from google.genai import types
from pydantic import ValidationError

from backend.schemas.extraction import ResumeExtraction
from backend.services.ai_providers.base import BaseAIProvider


class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
        self.timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "120"))

        if not self.api_key:
            self._available = False
            self.client = None
        else:
            self.client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(timeout=int(self.timeout * 1000)),
            )
            self._available = True

    @property
    def provider_name(self) -> str:
        return "gemini"

    def is_available(self) -> bool:
        return self._available

    def _prompt(self, resume_text: str) -> str:
        return f"""Extract a resume into JSON. Use ONLY facts explicitly present in the resume.
Never infer or guess technologies, employers, degrees, dates, certifications, or contact details.
Do NOT infer technologies, frameworks, databases, or programming languages.
Do NOT infer skills from project descriptions unless the technology or skill is explicitly mentioned.
Do NOT turn generic project descriptions into invented technologies.
Do NOT turn achievements into projects.
Do NOT turn projects into work experience.
The skills array must contain only flat skill names explicitly mentioned in the text.
A project is included only when the resume identifies it as a project. Work experience is only actual employment or internships.
Return JSON only matching the schema exactly.
For projects use objects with name, description, technologies. For education use institution, degree, field, dates.
For work_experience use company, title, description, dates. Do not add commentary.
If information is absent, return an empty string or empty array.

RESUME TEXT:
{resume_text[:30000]}"""

    def extract_resume(self, resume_text: str) -> ResumeExtraction:
        if not resume_text.strip():
            raise ValueError("Resume text is empty")

        if not self._available:
            raise RuntimeError("Gemini API key is not configured or service is unavailable")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=self._prompt(resume_text),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=ResumeExtraction.model_json_schema(),
                ),
            )

            if response.parsed is not None:
                return ResumeExtraction.model_validate(response.parsed)

            raw = response.text
            if not raw:
                raise RuntimeError("Gemini returned an empty response")
            return ResumeExtraction.model_validate_json(raw)

        except ValidationError as exc:
            raise RuntimeError(f"Gemini returned invalid structured output: {exc}") from exc
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                raise
            raise RuntimeError(f"Gemini API error: {exc}") from exc

    def embed_text(self, text: str) -> List[float]:
        if not self._available:
            raise RuntimeError("Gemini API key is not configured or service is unavailable")

        try:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text,
            )
            embeddings = response.embeddings or []
            if not embeddings or not embeddings[0].values:
                raise RuntimeError("Gemini returned empty embedding")
            return list(embeddings[0].values)
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                raise
            raise RuntimeError(f"Gemini embedding failed: {exc}") from exc
