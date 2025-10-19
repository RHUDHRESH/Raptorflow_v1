from typing import List
import numpy as np

try:
    from google.generativeai import embeddings
except ImportError:  # pragma: no cover
    embeddings = None

EMBEDDING_SIZE = 1536

def generate_embedding(text: str) -> List[float]:
    """Generate an embedding vector for the supplied text."""
    if embeddings is None:
        raise RuntimeError("Embedding client is not available")
    response = embeddings.embed_content(model="models/text-embedding-004", content=text)
    vector = response.get("embedding")
    if vector is None:
        raise RuntimeError("Failed to generate embedding")
    return vector


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    if not a.any() or not b.any():
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
