"""
RAG (Retrieval-Augmented Generation) Pipeline
==============================================

Integrates semantic search with AI generation:
- Retrieve relevant context from conversations
- Augment AI prompts with context
- Track context usage and relevance
- Optimize prompt construction
- Generate context-aware responses

Supports:
- Single conversation context
- Cross-conversation retrieval
- Multi-source context mixing
- Dynamic context window sizing
"""

import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from backend.utils.embedding_service import get_embedding_service, SearchResult
from backend.utils.conversation_manager import get_conversation_manager, Message

logger = logging.getLogger(__name__)


@dataclass
class RetrievedContext:
    """Retrieved context for RAG"""
    query: str
    similar_messages: List[SearchResult]
    recent_messages: List[Message]
    conversation_metadata: Dict[str, Any]
    total_tokens: int


@dataclass
class AugmentedPrompt:
    """Augmented prompt with context"""
    original_query: str
    context_summary: str
    full_prompt: str
    context_sources: int
    context_tokens: int
    augmentation_type: str  # 'recent', 'semantic', 'hybrid'


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline
    """

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.conversation_manager = get_conversation_manager()
        self.max_context_tokens = 2000  # Max tokens for context
        self.recent_messages_window = 5

    async def retrieve_context(
        self,
        query: str,
        conversation_id: str,
        include_recent: bool = True,
        include_semantic: bool = True,
        semantic_limit: int = 3,
        semantic_threshold: float = 0.6,
    ) -> RetrievedContext:
        """
        Retrieve context for RAG pipeline

        Args:
            query: User query
            conversation_id: Current conversation
            include_recent: Include recent messages
            include_semantic: Include semantic search results
            semantic_limit: Max semantic results
            semantic_threshold: Min similarity score

        Returns:
            RetrievedContext with all retrieved information
        """
        try:
            logger.info(f"Retrieving context for query: {query[:50]}...")

            similar_messages = []
            recent_messages = []

            # Retrieve recent messages
            if include_recent:
                recent_messages = await self.conversation_manager.get_recent_messages(
                    conversation_id=conversation_id,
                    limit=self.recent_messages_window,
                )
                logger.info(f"Retrieved {len(recent_messages)} recent messages")

            # Semantic search
            if include_semantic:
                similar_messages = await self.embedding_service.semantic_search(
                    query=query,
                    conversation_id=conversation_id,
                    limit=semantic_limit,
                    threshold=semantic_threshold,
                )
                logger.info(f"Found {len(similar_messages)} similar messages")

            # Get conversation metadata
            conversation = await self.conversation_manager.get_conversation(
                conversation_id=conversation_id,
                user_id="",  # Will be set by caller
                org_id="",   # Will be set by caller
            )

            # Calculate total tokens
            total_tokens = len(similar_messages) + len(recent_messages) * 100  # Rough estimate

            context = RetrievedContext(
                query=query,
                similar_messages=similar_messages,
                recent_messages=recent_messages,
                conversation_metadata=conversation.__dict__ if conversation else {},
                total_tokens=total_tokens,
            )

            return context

        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return RetrievedContext(
                query=query,
                similar_messages=[],
                recent_messages=[],
                conversation_metadata={},
                total_tokens=0,
            )

    async def augment_prompt(
        self,
        query: str,
        context: RetrievedContext,
        augmentation_type: str = "hybrid",
    ) -> AugmentedPrompt:
        """
        Augment prompt with retrieved context

        Args:
            query: Original user query
            context: Retrieved context
            augmentation_type: 'recent', 'semantic', or 'hybrid'

        Returns:
            AugmentedPrompt with full augmented text
        """
        try:
            logger.info(f"Augmenting prompt with {augmentation_type} strategy")

            # Build context summary
            context_parts = []

            # Add recent messages context
            if context.recent_messages and augmentation_type in ["recent", "hybrid"]:
                recent_context = "## Recent Discussion\n"
                for msg in context.recent_messages[-3:]:  # Last 3 messages
                    role = "User" if msg.role == "user" else "Assistant"
                    recent_context += f"**{role}**: {msg.content[:200]}...\n"
                context_parts.append(recent_context)

            # Add semantic context
            if context.similar_messages and augmentation_type in ["semantic", "hybrid"]:
                semantic_context = "## Related Previous Discussion\n"
                for result in context.similar_messages[:2]:  # Top 2 similar
                    similarity_pct = int(result.similarity_score * 100)
                    semantic_context += f"**(Relevance: {similarity_pct}%)** {result.content[:150]}...\n"
                context_parts.append(semantic_context)

            # Build full prompt
            context_summary = "\n".join(context_parts)

            full_prompt = f"""Based on the following context from our conversation, please answer the question.

{context_summary}

---

**Question**: {query}

Please provide a thoughtful response that considers the context above."""

            context_tokens = sum(
                len(msg.content.split()) for msg in context.recent_messages
            ) * 1.3  # Rough token estimate

            return AugmentedPrompt(
                original_query=query,
                context_summary=context_summary,
                full_prompt=full_prompt,
                context_sources=len(context.similar_messages) + len(context.recent_messages),
                context_tokens=int(context_tokens),
                augmentation_type=augmentation_type,
            )

        except Exception as e:
            logger.error(f"Prompt augmentation failed: {e}")
            # Return non-augmented prompt
            return AugmentedPrompt(
                original_query=query,
                context_summary="",
                full_prompt=query,
                context_sources=0,
                context_tokens=0,
                augmentation_type="none",
            )

    async def generate_with_context(
        self,
        query: str,
        conversation_id: str,
        user_id: str,
        org_id: str,
        ai_generator: callable,
    ) -> Dict[str, Any]:
        """
        Full RAG pipeline: retrieve context -> augment prompt -> generate

        Args:
            query: User query
            conversation_id: Current conversation
            user_id: User ID
            org_id: Organization ID
            ai_generator: Async function to generate response

        Returns:
            Generation result with metadata
        """
        try:
            logger.info("Starting RAG pipeline")

            # Step 1: Retrieve context
            context = await self.retrieve_context(
                query=query,
                conversation_id=conversation_id,
                include_recent=True,
                include_semantic=True,
            )

            # Step 2: Augment prompt
            augmented = await self.augment_prompt(
                query=query,
                context=context,
                augmentation_type="hybrid",
            )

            # Step 3: Generate response with augmented prompt
            logger.info("Generating response with augmented prompt")
            response = await ai_generator(augmented.full_prompt)

            return {
                "query": query,
                "response": response,
                "context_used": augmented.context_sources > 0,
                "context_sources": augmented.context_sources,
                "similar_messages": len(context.similar_messages),
                "recent_messages": len(context.recent_messages),
                "augmentation_type": augmented.augmentation_type,
                "context_tokens": augmented.context_tokens,
                "metadata": {
                    "context_summary": augmented.context_summary,
                    "original_prompt": augmented.original_prompt,
                },
            }

        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}")
            # Fallback: generate without context
            response = await ai_generator(query)
            return {
                "query": query,
                "response": response,
                "context_used": False,
                "error": str(e),
            }

    async def evaluate_context_relevance(
        self,
        query: str,
        context: RetrievedContext,
    ) -> Dict[str, Any]:
        """
        Evaluate how relevant retrieved context is

        Args:
            query: Original query
            context: Retrieved context

        Returns:
            Relevance metrics
        """
        try:
            # Calculate average similarity
            if context.similar_messages:
                avg_similarity = sum(
                    m.similarity_score for m in context.similar_messages
                ) / len(context.similar_messages)
            else:
                avg_similarity = 0

            # Context quality score (0-100)
            # Based on: number of sources, similarity, recency
            quality_score = (
                (len(context.similar_messages) / 5) * 30 +  # Similar messages
                (avg_similarity * 40) +  # Similarity score
                (len(context.recent_messages) / 5) * 30  # Recency
            )

            return {
                "quality_score": min(100, int(quality_score)),
                "avg_similarity": float(avg_similarity),
                "context_sources": len(context.similar_messages) + len(context.recent_messages),
                "is_relevant": quality_score > 30,
                "recommendation": (
                    "Excellent context" if quality_score > 70
                    else "Good context" if quality_score > 40
                    else "Limited context available"
                ),
            }

        except Exception as e:
            logger.error(f"Relevance evaluation failed: {e}")
            return {
                "quality_score": 0,
                "error": str(e),
            }

    async def optimize_context_window(
        self,
        context: RetrievedContext,
        max_tokens: int = 2000,
    ) -> RetrievedContext:
        """
        Optimize context to fit within token limit

        Args:
            context: Retrieved context
            max_tokens: Maximum tokens allowed

        Returns:
            Optimized context (subset of original)
        """
        try:
            # Estimate tokens
            total_tokens = 0

            # Count semantic results
            semantic_count = 0
            for msg in context.similar_messages:
                token_estimate = len(msg.content.split()) * 1.3
                if total_tokens + token_estimate <= max_tokens:
                    total_tokens += token_estimate
                    semantic_count += 1
                else:
                    break

            # Count recent messages
            recent_count = 0
            for msg in context.recent_messages:
                token_estimate = len(msg.content.split()) * 1.3
                if total_tokens + token_estimate <= max_tokens:
                    total_tokens += token_estimate
                    recent_count += 1
                else:
                    break

            logger.info(
                f"Optimized context: {semantic_count} semantic, "
                f"{recent_count} recent ({total_tokens} tokens)"
            )

            return RetrievedContext(
                query=context.query,
                similar_messages=context.similar_messages[:semantic_count],
                recent_messages=context.recent_messages[:recent_count],
                conversation_metadata=context.conversation_metadata,
                total_tokens=int(total_tokens),
            )

        except Exception as e:
            logger.error(f"Context optimization failed: {e}")
            return context


# Singleton instance
_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance"""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
