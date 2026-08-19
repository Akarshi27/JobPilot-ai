import json
import os
from typing import List

import openai
from pydantic import ValidationError

from backend.schemas.extraction import ResumeExtraction
from backend.services.ai_providers.base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "120"))
        
        if not self.api_key:
            self._available = False
        else:
            self.client = openai.OpenAI(api_key=self.api_key, timeout=self.timeout)
            self._available = True

    @property
    def provider_name(self) -> str:
        return "openai"

    def is_available(self) -> bool:
        return self._available

    def _prompt(self, resume_text: str) -> str:
        return f"""Extract a resume into JSON. Use ONLY facts explicitly present in the resume.
Never infer or guess technologies, employers, degrees, dates, certifications, or contact details.
The skills array must contain only flat skill names explicitly mentioned in the text.
A project is included only when the resume identifies it as a project. Work experience is only actual employment or internships.
Return JSON only matching the schema exactly.
For projects use objects with name, description, technologies. For education use institution, degree, field, dates.
For work_experience use company, title, description, dates. Do not add commentary.

RESUME TEXT:
{resume_text[:30000]}"""

    def extract_resume(self, resume_text: str) -> ResumeExtraction:
        if not resume_text.strip():
            raise ValueError("Resume text is empty")
            
        if not self._available:
            raise RuntimeError("OpenAI API key is not configured or service is unavailable")

        try:
            # We enforce structured output via Response Format (beta parsing)
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise resume extraction assistant."},
                    {"role": "user", "content": self._prompt(resume_text)}
                ],
                response_format=ResumeExtraction,
            )
            
            parsed = response.choices[0].message.parsed
            if not parsed:
                # If parsing fails, fall back to string and parse manually
                raw = response.choices[0].message.content
                if not raw:
                    raise RuntimeError("OpenAI returned an empty response")
                return ResumeExtraction.model_validate_json(raw)
            return parsed
            
        except openai.OpenAIError as exc:
            raise RuntimeError(f"OpenAI API error: {exc}") from exc
        except ValidationError as exc:
            raise RuntimeError(f"OpenAI returned invalid structured output: {exc}") from exc

    def embed_text(self, text: str) -> List[float]:
        if not self._available:
            raise RuntimeError("OpenAI API key is not configured or service is unavailable")
            
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except openai.OpenAIError as exc:
            raise RuntimeError(f"OpenAI embedding failed: {exc}") from exc
