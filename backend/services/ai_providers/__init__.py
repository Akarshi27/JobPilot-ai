import os
from typing import Optional

from backend.services.ai_providers.base import BaseAIProvider
from backend.services.ai_providers.ollama_provider import OllamaProvider
from backend.services.ai_providers.openai_provider import OpenAIProvider


_provider_instance: Optional[BaseAIProvider] = None

def get_ai_provider() -> BaseAIProvider:
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_name = os.getenv("AI_PROVIDER", "ollama").lower()
    
    if provider_name == "openai":
        _provider_instance = OpenAIProvider()
    elif provider_name == "ollama":
        _provider_instance = OllamaProvider()
    else:
        raise ValueError(f"Unknown AI_PROVIDER: {provider_name}")
        
    return _provider_instance
