"""
Vector Embedding Service
========================

Generates and manages vector embeddings for conversations:
- Generate embeddings from text using OpenAI API
- Store embeddings in pgvector
- Semantic search across messages
- Find similar messages and conversations
- Optimize embedding generation and caching

Integrates with:
- OpenAI Embeddings API
- PostgreSQL pgvector extension
- Supabase database
"""

import logging
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json

import openai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from backend.utils.supabase_client import get_supabase_client
from backend.utils.cloud_provider import get_cloud_provider

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    text: str
    embedding: List[float]
    model: str
    tokens: int


@dataclass
class SearchResult:
    """Result of semantic search"""
    message_id: str
    conversation_id: str
    content: str
    role: str
    similarity_score: float
    created_at: str


class EmbeddingService:
    """
    Manages vector embeddings for semantic search
    """

    def __init__(self):
        self.supabase = get_supabase_client()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = "text-embedding-3-small"  # Fast & efficient
        self.embedding_dimension = 1536

        # Initialize OpenAI client
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("OPENAI_API_KEY not set for embeddings")

    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> Optional[EmbeddingResult]:
        """
        Generate embedding for text using OpenAI API

        Args:
            text: Text to embed
            model: Optional model override (default: text-embedding-3-small)

        Returns:
            EmbeddingResult with embedding vector and metadata

        Raises:
            ValueError: If embedding generation fails
        """
        try:
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")

            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")

            model = model or self.embedding_model

            # Generate embedding
            logger.info(f"Generating embedding for text: {text[:50]}...")

            response = openai.Embedding.create(
                input=text,
                model=model,
            )

            embedding = response["data"][0]["embedding"]
            tokens = response["usage"]["prompt_tokens"]

            logger.info(f"Generated embedding with {len(embedding)} dimensions")

            return EmbeddingResult(
                text=text,
                embedding=embedding,
                model=model,
                tokens=tokens,
            )

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise ValueError(f"Failed to generate embedding: {e}")

    async def store_embedding(
        self,
        message_id: str,
        conversation_id: str,
        embedding: List[float],
        model: str = "text-embedding-3-small",
    ) -> bool:
        """
        Store embedding in pgvector database

        Args:
            message_id: Message UUID
            conversation_id: Conversation UUID
            embedding: Vector embedding
            model: Embedding model used

        Returns:
            True if stored successfully

        Raises:
            ValueError: If storage fails
        """
        try:
            # Store in message_embeddings table
            response = self.supabase.table("message_embeddings").insert({
                "message_id": message_id,
                "conversation_id": conversation_id,
                "embedding": embedding,
                "embedding_model": model,
                "content_length": len(embedding),
            }).execute()

            if not response.data:
                raise ValueError("Failed to store embedding")

            logger.info(f"Stored embedding for message: {message_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            raise ValueError(f"Failed to store embedding: {e}")

    async def embed_and_store(
        self,
        message_id: str,
        conversation_id: str,
        text: str,
    ) -> bool:
        """
        Generate embedding and store it (combined operation)

        Args:
            message_id: Message UUID
            conversation_id: Conversation UUID
            text: Message text to embed

        Returns:
            True if successful
        """
        try:
            # Generate embedding
            result = await self.generate_embedding(text)

            if not result:
                return False

            # Store embedding
            await self.store_embedding(
                message_id=message_id,
                conversation_id=conversation_id,
                embedding=result.embedding,
                model=result.model,
            )

            return True

        except Exception as e:
            logger.error(f"Failed to embed and store: {e}")
            return False

    async def semantic_search(
        self,
        query: str,
        conversation_id: str,
        limit: int = 5,
        threshold: float = 0.5,
    ) -> List[SearchResult]:
        """
        Search for similar messages in a conversation

        Args:
            query: Search query text
            conversation_id: Conversation to search in
            limit: Max results
            threshold: Minimum similarity score (0-1)

        Returns:
            List of SearchResult objects ranked by similarity
        """
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            if not query_embedding:
                return []

            # Get all embeddings in conversation
            response = self.supabase.table("message_embeddings").select(
                "id, message_id, embedding, messages:conversation_messages(id, conversation_id, role, content, created_at)"
            ).eq("conversation_id", conversation_id).execute()

            if not response.data:
                logger.info(f"No embeddings found for conversation: {conversation_id}")
                return []

            # Calculate similarities
            results = []
            query_vec = np.array(query_embedding.embedding).reshape(1, -1)

            for item in response.data:
                try:
                    msg = item.get("messages", {})
                    if not msg:
                        continue

                    embedding_vec = np.array(item["embedding"]).reshape(1, -1)
                    similarity = cosine_similarity(query_vec, embedding_vec)[0][0]

                    if similarity >= threshold:
                        results.append(SearchResult(
                            message_id=msg.get("id"),
                            conversation_id=msg.get("conversation_id"),
                            content=msg.get("content"),
                            role=msg.get("role"),
                            similarity_score=float(similarity),
                            created_at=msg.get("created_at"),
                        ))

                except Exception as e:
                    logger.warning(f"Error processing embedding: {e}")
                    continue

            # Sort by similarity score
            results.sort(key=lambda x: x.similarity_score, reverse=True)

            # Return top results
            return results[:limit]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    async def semantic_search_global(
        self,
        query: str,
        org_id: str,
        limit: int = 10,
        threshold: float = 0.5,
    ) -> List[SearchResult]:
        """
        Search for similar messages across all org conversations

        Args:
            query: Search query
            org_id: Organization ID (for scoping)
            limit: Max results
            threshold: Minimum similarity

        Returns:
            Top matching messages from all conversations
        """
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            if not query_embedding:
                return []

            # Get embeddings from all org conversations
            # Note: This requires a more complex query with joins
            # For simplicity, we'll do it in Python
            response = self.supabase.table("message_embeddings").select(
                "id, message_id, embedding, messages:conversation_messages(id, role, content, created_at, conversations:conversations(id, org_id))"
            ).execute()

            if not response.data:
                return []

            results = []
            query_vec = np.array(query_embedding.embedding).reshape(1, -1)

            for item in response.data:
                try:
                    msg = item.get("messages", {})
                    conv = msg.get("conversations", {})

                    # Check org scope
                    if conv.get("org_id") != org_id:
                        continue

                    embedding_vec = np.array(item["embedding"]).reshape(1, -1)
                    similarity = cosine_similarity(query_vec, embedding_vec)[0][0]

                    if similarity >= threshold:
                        results.append(SearchResult(
                            message_id=msg.get("id"),
                            conversation_id=conv.get("id"),
                            content=msg.get("content"),
                            role=msg.get("role"),
                            similarity_score=float(similarity),
                            created_at=msg.get("created_at"),
                        ))

                except Exception as e:
                    logger.warning(f"Error in global search: {e}")
                    continue

            # Sort and return top results
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Global semantic search failed: {e}")
            return []

    async def delete_embedding(self, message_id: str) -> bool:
        """
        Delete embedding for a message

        Args:
            message_id: Message UUID

        Returns:
            True if deleted
        """
        try:
            self.supabase.table("message_embeddings").delete().eq(
                "message_id", message_id
            ).execute()

            logger.info(f"Deleted embedding for message: {message_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete embedding: {e}")
            return False

    async def get_embedding(self, message_id: str) -> Optional[List[float]]:
        """
        Get stored embedding for a message

        Args:
            message_id: Message UUID

        Returns:
            Embedding vector or None
        """
        try:
            response = self.supabase.table("message_embeddings").select(
                "embedding"
            ).eq("message_id", message_id).execute()

            if not response.data:
                return None

            return response.data[0]["embedding"]

        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None

    async def batch_embed_messages(
        self,
        conversation_id: str,
        message_ids: List[str],
        texts: List[str],
    ) -> Dict[str, bool]:
        """
        Batch generate and store embeddings for multiple messages

        Args:
            conversation_id: Conversation ID
            message_ids: List of message UUIDs
            texts: List of message texts (same length as message_ids)

        Returns:
            Dict mapping message_id to success status
        """
        if len(message_ids) != len(texts):
            raise ValueError("message_ids and texts must be same length")

        results = {}

        for msg_id, text in zip(message_ids, texts):
            try:
                success = await self.embed_and_store(
                    message_id=msg_id,
                    conversation_id=conversation_id,
                    text=text,
                )
                results[msg_id] = success
            except Exception as e:
                logger.error(f"Failed to embed message {msg_id}: {e}")
                results[msg_id] = False

        return results

    async def compute_embedding_stats(
        self,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """
        Compute statistics about embeddings in a conversation

        Args:
            conversation_id: Conversation UUID

        Returns:
            Stats dict with count, avg_similarity, etc
        """
        try:
            response = self.supabase.table("message_embeddings").select(
                "id, embedding"
            ).eq("conversation_id", conversation_id).execute()

            if not response.data or len(response.data) < 2:
                return {
                    "total_embeddings": len(response.data or []),
                    "avg_similarity": 0,
                    "message": "Need at least 2 embeddings"
                }

            embeddings = [np.array(item["embedding"]) for item in response.data]

            # Compute pairwise similarities
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    sim = cosine_similarity(
                        embeddings[i].reshape(1, -1),
                        embeddings[j].reshape(1, -1)
                    )[0][0]
                    similarities.append(float(sim))

            avg_similarity = np.mean(similarities) if similarities else 0

            return {
                "total_embeddings": len(embeddings),
                "avg_similarity": float(avg_similarity),
                "min_similarity": float(np.min(similarities)),
                "max_similarity": float(np.max(similarities)),
                "std_similarity": float(np.std(similarities)),
            }

        except Exception as e:
            logger.error(f"Failed to compute stats: {e}")
            return {"error": str(e)}


# Singleton instance
_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service
