"""
Service factory module for creating mode-appropriate service instances.

This module handles instantiation of all services (LLM, embeddings, vector DB, cache)
based on the execution mode configuration. It abstracts away provider-specific logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.core.config import (
    CacheProvider,
    EmbeddingProvider,
    ExecutionMode,
    LLMProvider,
    VectorDBProvider,
    settings,
)


# ============================================================================
# LLM SERVICE FACTORY
# ============================================================================


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    async def generate_streaming(self, prompt: str, max_tokens: int = 2000):
        """Stream text generation."""
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass


class OllamaLLMService(BaseLLMService):
    """Ollama LLM service for dev mode."""

    def __init__(self):
        """Initialize Ollama client."""
        try:
            import ollama
            self.client = ollama
            self.model = settings.OLLAMA_MODEL
            self.base_url = settings.OLLAMA_BASE_URL
        except ImportError:
            raise ImportError(
                "ollama package required for dev mode. "
                "Install with: pip install ollama"
            )

    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate text using Ollama."""
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False,
        )
        return response.get("response", "")

    async def generate_streaming(self, prompt: str, max_tokens: int = 2000):
        """Stream text generation from Ollama."""
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=True,
        )
        for chunk in response:
            yield chunk.get("response", "")

    async def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation for Ollama)."""
        # Rough estimate: 1 token ≈ 4 characters for English
        return len(text) // 4


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service for cloud mode."""

    def __init__(self):
        """Initialize OpenAI client."""
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            self.fast_model = settings.OPENAI_FAST_MODEL
        except ImportError:
            raise ImportError(
                "openai package required for cloud mode. "
                "Install with: pip install openai"
            )

    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate text using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content or ""

    async def generate_streaming(self, prompt: str, max_tokens: int = 2000):
        """Stream text generation from OpenAI."""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def count_tokens(self, text: str) -> int:
        """Count tokens using OpenAI tokenizer."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: rough estimate
            return len(text) // 4


def create_llm_service() -> BaseLLMService:
    """Factory function to create appropriate LLM service."""
    if settings.is_using_ollama:
        return OllamaLLMService()
    elif settings.is_using_openai:
        return OpenAILLMService()
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


# ============================================================================
# EMBEDDING SERVICE FACTORY
# ============================================================================


class BaseEmbeddingService(ABC):
    """Abstract base class for embedding services."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Embed single text."""
        pass

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts."""
        pass


class OllamaEmbeddingService(BaseEmbeddingService):
    """Ollama embedding service for dev mode."""

    def __init__(self):
        """Initialize Ollama embedding client."""
        try:
            import ollama
            self.client = ollama
            self.model = settings.OLLAMA_EMBEDDING_MODEL
        except ImportError:
            raise ImportError(
                "ollama package required for dev mode. "
                "Install with: pip install ollama"
            )

    async def embed_text(self, text: str) -> list[float]:
        """Embed single text using Ollama."""
        response = self.client.embed(
            model=self.model,
            input=text,
        )
        return response["embeddings"][0]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts using Ollama."""
        response = self.client.embed(
            model=self.model,
            input=texts,
        )
        return response["embeddings"]


class OpenAIEmbeddingService(BaseEmbeddingService):
    """OpenAI embedding service for cloud mode."""

    def __init__(self):
        """Initialize OpenAI embedding client."""
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.EMBEDDING_MODEL
        except ImportError:
            raise ImportError(
                "openai package required for cloud mode. "
                "Install with: pip install openai"
            )

    async def embed_text(self, text: str) -> list[float]:
        """Embed single text using OpenAI."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts using OpenAI."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]


def create_embedding_service() -> BaseEmbeddingService:
    """Factory function to create appropriate embedding service."""
    if settings.EMBEDDING_PROVIDER == EmbeddingProvider.OLLAMA:
        return OllamaEmbeddingService()
    elif settings.EMBEDDING_PROVIDER == EmbeddingProvider.OPENAI:
        return OpenAIEmbeddingService()
    else:
        raise ValueError(f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}")


# ============================================================================
# VECTOR DATABASE FACTORY
# ============================================================================


class BaseVectorDBService(ABC):
    """Abstract base class for vector database services."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to vector database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from vector database."""
        pass

    @abstractmethod
    async def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: Optional[list[Dict[str, Any]]] = None,
        ids: Optional[list[str]] = None,
    ) -> None:
        """Add documents to vector database."""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> list[Dict[str, Any]]:
        """Search for similar documents."""
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> None:
        """Delete documents by ID."""
        pass


class ChromaDBVectorService(BaseVectorDBService):
    """ChromaDB vector service for dev mode."""

    def __init__(self):
        """Initialize ChromaDB client."""
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMADB_PATH
            )
            self.collection = None
        except ImportError:
            raise ImportError(
                "chromadb package required for dev mode vector DB. "
                "Install with: pip install chromadb"
            )

    async def connect(self) -> None:
        """Initialize ChromaDB collection."""
        self.collection = self.chroma_client.get_or_create_collection(
            name="raptorflow_vectors",
            metadata={"hnsw:space": "cosine"}
        )

    async def disconnect(self) -> None:
        """ChromaDB cleanup (no-op)."""
        pass

    async def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: Optional[list[Dict[str, Any]]] = None,
        ids: Optional[list[str]] = None,
    ) -> None:
        """Add documents to ChromaDB."""
        if self.collection is None:
            await self.connect()

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas or [{"source": "raptorflow"} for _ in documents],
            ids=ids or [f"doc_{i}" for i in range(len(documents))],
        )

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> list[Dict[str, Any]]:
        """Search ChromaDB."""
        if self.collection is None:
            await self.connect()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters,
        )

        documents = []
        for i, doc_id in enumerate(results["ids"][0]):
            documents.append({
                "id": doc_id,
                "document": results["documents"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i],
            })
        return documents

    async def delete(self, ids: list[str]) -> None:
        """Delete documents from ChromaDB."""
        if self.collection:
            self.collection.delete(ids=ids)


class SupabaseVectorService(BaseVectorDBService):
    """Supabase pgvector service for cloud mode."""

    def __init__(self):
        """Initialize Supabase vector client."""
        try:
            from supabase import AsyncClient, create_client
            self.supabase: AsyncClient = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY,
            )
        except ImportError:
            raise ImportError(
                "supabase package required for cloud mode vector DB. "
                "Install with: pip install supabase"
            )

    async def connect(self) -> None:
        """Initialize Supabase connection."""
        # Supabase connects automatically
        pass

    async def disconnect(self) -> None:
        """Disconnect from Supabase."""
        pass

    async def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: Optional[list[Dict[str, Any]]] = None,
        ids: Optional[list[str]] = None,
    ) -> None:
        """Add documents to Supabase pgvector."""
        rows = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            rows.append({
                "id": ids[i] if ids else f"doc_{i}",
                "content": doc,
                "embedding": embedding,
                "metadata": metadatas[i] if metadatas else {"source": "raptorflow"},
            })

        await self.supabase.table("documents").insert(rows).execute()

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> list[Dict[str, Any]]:
        """Search Supabase pgvector."""
        # Using RPC call to Supabase function for similarity search
        results = await self.supabase.rpc(
            "search_documents",
            {
                "query_embedding": query_embedding,
                "match_count": top_k,
            }
        ).execute()

        return results.data if results.data else []

    async def delete(self, ids: list[str]) -> None:
        """Delete documents from Supabase."""
        await self.supabase.table("documents").delete().in_("id", ids).execute()


def create_vector_db_service() -> BaseVectorDBService:
    """Factory function to create appropriate vector DB service."""
    if settings.VECTOR_DB_PROVIDER == VectorDBProvider.CHROMADB:
        return ChromaDBVectorService()
    elif settings.VECTOR_DB_PROVIDER == VectorDBProvider.SUPABASE_PGVECTOR:
        return SupabaseVectorService()
    else:
        raise ValueError(
            f"Unsupported vector DB provider: {settings.VECTOR_DB_PROVIDER}"
        )


# ============================================================================
# CACHE SERVICE FACTORY
# ============================================================================


class BaseCacheService(ABC):
    """Abstract base class for cache services."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache."""
        pass


class InMemoryCacheService(BaseCacheService):
    """In-memory cache service for dev mode."""

    def __init__(self):
        """Initialize in-memory cache."""
        self.cache: Dict[str, tuple[Any, Optional[float]]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from in-memory cache."""
        import time
        if key in self.cache:
            value, expiry = self.cache[key]
            if expiry is None or time.time() < expiry:
                return value
            else:
                del self.cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in in-memory cache."""
        import time
        expiry = None if ttl is None else time.time() + ttl
        self.cache[key] = (value, expiry)

    async def delete(self, key: str) -> None:
        """Delete key from in-memory cache."""
        if key in self.cache:
            del self.cache[key]

    async def clear(self) -> None:
        """Clear in-memory cache."""
        self.cache.clear()


class RedisCacheService(BaseCacheService):
    """Redis cache service for cloud mode."""

    def __init__(self):
        """Initialize Redis client."""
        try:
            import redis
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
        except ImportError:
            raise ImportError(
                "redis package required for cloud mode cache. "
                "Install with: pip install redis"
            )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        import json
        value = self.redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis."""
        import json
        try:
            json_value = json.dumps(value)
        except TypeError:
            json_value = str(value)

        if ttl:
            self.redis_client.setex(key, ttl, json_value)
        else:
            self.redis_client.set(key, json_value)

    async def delete(self, key: str) -> None:
        """Delete key from Redis."""
        self.redis_client.delete(key)

    async def clear(self) -> None:
        """Clear all Redis cache."""
        self.redis_client.flushdb()


def create_cache_service() -> BaseCacheService:
    """Factory function to create appropriate cache service."""
    if settings.CACHE_PROVIDER == CacheProvider.IN_MEMORY:
        return InMemoryCacheService()
    elif settings.CACHE_PROVIDER == CacheProvider.REDIS:
        return RedisCacheService()
    else:
        raise ValueError(f"Unsupported cache provider: {settings.CACHE_PROVIDER}")


# ============================================================================
# SERVICE MANAGER (Singleton)
# ============================================================================


class ServiceManager:
    """Centralized service manager for all mode-aware services."""

    _instance: Optional["ServiceManager"] = None
    _llm_service: Optional[BaseLLMService] = None
    _embedding_service: Optional[BaseEmbeddingService] = None
    _vector_db_service: Optional[BaseVectorDBService] = None
    _cache_service: Optional[BaseCacheService] = None

    def __new__(cls) -> "ServiceManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def llm(self) -> BaseLLMService:
        """Get LLM service (lazy load)."""
        if self._llm_service is None:
            self._llm_service = create_llm_service()
        return self._llm_service

    @property
    def embeddings(self) -> BaseEmbeddingService:
        """Get embedding service (lazy load)."""
        if self._embedding_service is None:
            self._embedding_service = create_embedding_service()
        return self._embedding_service

    @property
    def vector_db(self) -> BaseVectorDBService:
        """Get vector DB service (lazy load)."""
        if self._vector_db_service is None:
            self._vector_db_service = create_vector_db_service()
        return self._vector_db_service

    @property
    def cache(self) -> BaseCacheService:
        """Get cache service (lazy load)."""
        if self._cache_service is None:
            self._cache_service = create_cache_service()
        return self._cache_service

    async def initialize(self) -> None:
        """Initialize all services."""
        await self.vector_db.connect()

    async def shutdown(self) -> None:
        """Shutdown all services."""
        await self.vector_db.disconnect()
        await self.cache.clear()


# Global service manager instance
services = ServiceManager()
