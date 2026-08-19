import os
from unittest.mock import patch, MagicMock

import pytest

from backend.schemas.extraction import ResumeExtraction
from backend.services.ai_providers import get_ai_provider
from backend.services.ai_providers.ollama_provider import OllamaProvider
from backend.services.ai_providers.openai_provider import OpenAIProvider
from backend.services.embedding_service import similarity
from backend.services.matching import semantic_match


@pytest.fixture(autouse=True)
def reset_provider_instance():
    import backend.services.ai_providers
    backend.services.ai_providers._provider_instance = None
    yield
    backend.services.ai_providers._provider_instance = None


@patch.dict(os.environ, {"AI_PROVIDER": "ollama"})
def test_ollama_provider_selection():
    provider = get_ai_provider()
    assert isinstance(provider, OllamaProvider)


@patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "fake-key"})
def test_openai_provider_selection():
    provider = get_ai_provider()
    assert isinstance(provider, OpenAIProvider)


@patch.dict(os.environ, {"AI_PROVIDER": "invalid"})
def test_invalid_provider():
    with pytest.raises(ValueError, match="Unknown AI_PROVIDER: invalid"):
        get_ai_provider()


@patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "fake-key"})
@patch("openai.OpenAI")
def test_structured_resume_extraction_validation(mock_openai):
    provider = get_ai_provider()
    
    mock_client = MagicMock()
    provider.client = mock_client
    
    mock_parsed = ResumeExtraction(
        candidate_name="Test User",
        email="test@test.com",
        skills=["Python", "FastAPI"]
    )
    
    mock_response = MagicMock()
    mock_response.choices[0].message.parsed = mock_parsed
    mock_client.beta.chat.completions.parse.return_value = mock_response
    
    result = provider.extract_resume("My name is Test User. Python and FastAPI.")
    assert result.candidate_name == "Test User"
    assert result.skills == ["Python", "FastAPI"]


@patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": ""})
def test_missing_openai_api_key():
    provider = get_ai_provider()
    assert not provider.is_available()
    with pytest.raises(RuntimeError, match="OpenAI API key is not configured or service is unavailable"):
        provider.extract_resume("test")


@patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "fake-key"})
@patch("openai.OpenAI")
def test_embedding_provider_selection(mock_openai):
    provider = get_ai_provider()
    mock_client = MagicMock()
    provider.client = mock_client
    
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    mock_client.embeddings.create.return_value = mock_response
    
    emb = provider.embed_text("test text")
    assert emb == [0.1, 0.2, 0.3]


@patch("backend.services.matching.embed_text")
def test_semantic_paraphrase_matching(mock_embed):
    def mock_embed_text(text):
        if "RESTful APIs" in text or "backend HTTP services" in text:
            return [1.0, 0.0, 0.0]
        return [0.0, 1.0, 0.0]
    
    mock_embed.side_effect = mock_embed_text
    
    res = semantic_match(
        candidate_text="built RESTful APIs using FastAPI",
        job_text="experience developing backend HTTP services",
        candidate_skills=["FastAPI"],
        required_skills=["Python"],
    )
    
    assert res["semantic_score"] > 80.0


@patch.dict(os.environ, {"AI_PROVIDER": "ollama"})
@patch("requests.post")
def test_long_resume_handling_and_timeout(mock_post):
    import requests
    provider = get_ai_provider()
    
    mock_post.side_effect = requests.exceptions.Timeout("Timeout occurred")
    
    with pytest.raises(RuntimeError, match="unavailable or invalid"):
        provider.extract_resume("A" * 50000)


@patch.dict(os.environ, {"AI_PROVIDER": "ollama"})
@patch("requests.post")
def test_ai_unavailable_behavior(mock_post):
    import requests
    provider = get_ai_provider()
    
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
    
    with pytest.raises(RuntimeError, match="Ollama connection failed"):
        provider.extract_resume("test")
