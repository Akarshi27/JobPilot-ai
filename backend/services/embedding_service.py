import hashlib
import math
import re
from functools import lru_cache

from backend.services.ai_providers import get_ai_provider


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


@lru_cache(maxsize=2000)
def embed_text(text: str) -> list[float]:
    provider = get_ai_provider()
    try:
        return provider.embed_text(text)
    except Exception:
        return _fallback_embedding(text)


def similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return max(0.0, min(1.0, numerator / (left_norm * right_norm or 1.0)))