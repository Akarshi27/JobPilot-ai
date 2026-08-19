from abc import ABC, abstractmethod
from typing import Dict, Any, List

from backend.schemas.extraction import ResumeExtraction


class BaseAIProvider(ABC):
    """Abstract base class for AI providers (Ollama, OpenAI, etc.)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is currently available."""
        pass

    @abstractmethod
    def extract_resume(self, resume_text: str) -> ResumeExtraction:
        """Extract structured data from resume text."""
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for the given text."""
        pass
