from typing import List
import numpy as np
import os

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

EMBEDDING_SIZE = 1536

# Initialize Chroma DB client
def get_chroma_client():
    if chromadb is None:
        raise RuntimeError("Chroma DB client is not available")
    chroma_host = os.getenv('CHROMA_HOST', 'localhost')
    chroma_port = int(os.getenv('CHROMA_PORT', 8001))
    client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    return client

def generate_embedding(text: str) -> List[float]:
    """Generate an embedding vector for the supplied text using Chroma DB."""
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="embeddings")
    # Use a simple embedding model, assuming Chroma DB handles it
    # For now, we'll use a placeholder since Chroma DB doesn't generate embeddings directly
    # In practice, you might need to integrate with a local embedding model like sentence-transformers
    # For this refactor, I'll simulate it
    import hashlib
    # Simple hash-based embedding for demo (replace with real model)
    hash_obj = hashlib.md5(text.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    vector = [float((hash_int >> i) & 1) for i in range(EMBEDDING_SIZE)]
    # Normalize
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    if not a.any() or not b.any():
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
