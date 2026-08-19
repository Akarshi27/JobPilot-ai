import hashlib
import math
import os
import re

import requests


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

_ollama_available = True


def _fallback_embedding(text: str, dimensions: int = 256) -> list[float]:
    """Offline fallback using word and phrase features, never a fixed skill vocabulary."""
    vector = [0.0] * dimensions
    normalized = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    tokens = normalized.split()
    features = tokens + [" ".join(tokens[index:index + 2]) for index in range(len(tokens) - 1)]
    for feature in features:
        digest = hashlib.sha256(feature.encode()).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += 1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


from functools import lru_cache

@lru_cache(maxsize=2000)
def embed_text(text: str) -> list[float]:
    global _ollama_available
    if _ollama_available:
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBEDDING_MODEL, "prompt": text},
                timeout=1,
            )
            response.raise_for_status()
            embedding = response.json().get("embedding")
            if embedding:
                return embedding
        except requests.exceptions.ConnectionError:
            _ollama_available = False
        except (requests.RequestException, ValueError, TypeError):
            pass
    return _fallback_embedding(text)


def similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return max(0.0, min(1.0, numerator / (left_norm * right_norm or 1.0)))