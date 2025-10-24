"""
Embedding & Vector Search API Routes
=====================================

REST API endpoints for semantic search:
- Generate embeddings
- Store embeddings
- Search similar messages
- Get embedding statistics
- Batch embedding operations

Authentication required: JWT token
"""

import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request, Query, Body
from pydantic import BaseModel, Field

from backend.utils.embedding_service import get_embedding_service, SearchResult

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


# ==================== Request/Response Models ====================

class EmbedTextRequest(BaseModel):
    """Generate embedding request"""
    text: str = Field(..., min_length=1, max_length=10000)
    model: Optional[str] = Field(None, description="Optional model override")


class EmbedMessageRequest(BaseModel):
    """Store embedding for message"""
    message_id: str = Field(..., description="Message UUID")
    conversation_id: str = Field(..., description="Conversation UUID")
    text: str = Field(..., min_length=1, max_length=10000)


class EmbeddingResponse(BaseModel):
    """Embedding response"""
    text: str
    embedding_size: int
    model: str
    tokens_used: int


class SemanticSearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(5, ge=1, le=50)
    threshold: float = Field(0.5, ge=0, le=1)


class SearchResultResponse(BaseModel):
    """Single search result"""
    message_id: str
    conversation_id: str
    content: str
    role: str
    similarity_score: float
    created_at: str


class SearchResponse(BaseModel):
    """Search results response"""
    query: str
    results: List[SearchResultResponse]
    count: int


class EmbeddingStatsResponse(BaseModel):
    """Embedding statistics"""
    total_embeddings: int
    avg_similarity: float
    min_similarity: Optional[float] = None
    max_similarity: Optional[float] = None
    std_similarity: Optional[float] = None


# ==================== Endpoints ====================

@router.post("/embed-text", response_model=EmbeddingResponse)
async def embed_text(
    request: Request,
    payload: EmbedTextRequest,
) -> EmbeddingResponse:
    """
    Generate embedding for arbitrary text

    **Authentication**: Required (JWT token)

    **Request Body**:
    ```json
    {
      "text": "What is our marketing strategy?"
    }
    ```

    **Response**: Embedding metadata (vector not included for size)

    **Status Codes**:
    - 200: Embedding generated
    - 401: Not authenticated
    - 500: Generation failed
    """
    try:
        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
            )

        # Generate embedding
        service = get_embedding_service()
        result = await service.generate_embedding(
            text=payload.text,
            model=payload.model,
        )

        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate embedding",
            )

        return EmbeddingResponse(
            text=result.text,
            embedding_size=len(result.embedding),
            model=result.model,
            tokens_used=result.tokens,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to embed text: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate embedding",
        )


@router.post("/embed-and-store", response_model=Dict[str, Any])
async def embed_and_store(
    request: Request,
    payload: EmbedMessageRequest,
) -> Dict[str, Any]:
    """
    Generate and store embedding for a message

    **Request Body**:
    ```json
    {
      "message_id": "uuid",
      "conversation_id": "uuid",
      "text": "Message content to embed"
    }
    ```

    **Response**: Success status

    **Status Codes**:
    - 200: Embedding stored
    - 401: Not authenticated
    - 500: Failed
    """
    try:
        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        service = get_embedding_service()
        success = await service.embed_and_store(
            message_id=payload.message_id,
            conversation_id=payload.conversation_id,
            text=payload.text,
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store embedding",
            )

        return {
            "message_id": payload.message_id,
            "stored": True,
            "status": "Embedding generated and stored"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to embed and store: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to store embedding",
        )


@router.post("/semantic-search", response_model=SearchResponse)
async def semantic_search(
    request: Request,
    conversation_id: str = Query(..., description="Conversation UUID"),
    payload: SemanticSearchRequest = Body(...),
) -> SearchResponse:
    """
    Search for similar messages in a conversation

    **Query Parameters**:
    - conversation_id: Conversation UUID (required)

    **Request Body**:
    ```json
    {
      "query": "What about budget allocation?",
      "limit": 5,
      "threshold": 0.5
    }
    ```

    **Response**: Ranked list of similar messages

    **Status Codes**:
    - 200: Success
    - 401: Not authenticated
    - 404: Conversation not found
    """
    try:
        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        service = get_embedding_service()

        # Perform semantic search
        results = await service.semantic_search(
            query=payload.query,
            conversation_id=conversation_id,
            limit=payload.limit,
            threshold=payload.threshold,
        )

        return SearchResponse(
            query=payload.query,
            results=[
                SearchResultResponse(
                    message_id=r.message_id,
                    conversation_id=r.conversation_id,
                    content=r.content,
                    role=r.role,
                    similarity_score=r.similarity_score,
                    created_at=r.created_at,
                )
                for r in results
            ],
            count=len(results),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Search failed",
        )


@router.get("/semantic-search/global", response_model=SearchResponse)
async def semantic_search_global(
    request: Request,
    query: str = Query(..., min_length=1, max_length=1000),
    limit: int = Query(10, ge=1, le=100),
    threshold: float = Query(0.5, ge=0, le=1),
) -> SearchResponse:
    """
    Search across all conversations in organization

    **Query Parameters**:
    - query: Search text (required)
    - limit: Max results (1-100, default 10)
    - threshold: Min similarity (0-1, default 0.5)

    **Response**: Similar messages from any conversation

    **Status Codes**:
    - 200: Success
    - 401: Not authenticated
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        service = get_embedding_service()

        # Perform global search
        results = await service.semantic_search_global(
            query=query,
            org_id=org_id,
            limit=limit,
            threshold=threshold,
        )

        return SearchResponse(
            query=query,
            results=[
                SearchResultResponse(
                    message_id=r.message_id,
                    conversation_id=r.conversation_id,
                    content=r.content,
                    role=r.role,
                    similarity_score=r.similarity_score,
                    created_at=r.created_at,
                )
                for r in results
            ],
            count=len(results),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Global search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Search failed",
        )


@router.get("/embedding-stats", response_model=EmbeddingStatsResponse)
async def get_embedding_stats(
    request: Request,
    conversation_id: str = Query(..., description="Conversation UUID"),
) -> EmbeddingStatsResponse:
    """
    Get embedding statistics for a conversation

    **Query Parameters**:
    - conversation_id: Conversation UUID (required)

    **Response**: Statistics about embeddings

    **Status Codes**:
    - 200: Success
    - 401: Not authenticated
    """
    try:
        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        service = get_embedding_service()
        stats = await service.compute_embedding_stats(conversation_id)

        return EmbeddingStatsResponse(
            total_embeddings=stats.get("total_embeddings", 0),
            avg_similarity=stats.get("avg_similarity", 0),
            min_similarity=stats.get("min_similarity"),
            max_similarity=stats.get("max_similarity"),
            std_similarity=stats.get("std_similarity"),
        )

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get statistics",
        )


@router.delete("/embeddings/{message_id}")
async def delete_embedding(
    message_id: str,
    request: Request,
) -> Dict[str, str]:
    """
    Delete embedding for a message

    **Path Parameters**:
    - message_id: Message UUID

    **Response**: Confirmation

    **Status Codes**:
    - 200: Deleted
    - 401: Not authenticated
    """
    try:
        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        service = get_embedding_service()
        success = await service.delete_embedding(message_id)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete embedding",
            )

        return {"message": "Embedding deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete embedding: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete embedding",
        )


@router.post("/batch-embed")
async def batch_embed_messages(
    request: Request,
    payload: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Batch generate and store embeddings

    **Request Body**:
    ```json
    {
      "conversation_id": "uuid",
      "messages": [
        {
          "message_id": "uuid",
          "text": "Message 1"
        },
        {
          "message_id": "uuid",
          "text": "Message 2"
        }
      ]
    }
    ```

    **Response**: Results for each message

    **Status Codes**:
    - 200: Batch processed
    - 401: Not authenticated
    """
    try:
        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        conversation_id = payload.get("conversation_id")
        messages = payload.get("messages", [])

        if not conversation_id or not messages:
            raise HTTPException(
                status_code=400,
                detail="conversation_id and messages required",
            )

        message_ids = [m.get("message_id") for m in messages]
        texts = [m.get("text") for m in messages]

        service = get_embedding_service()
        results = await service.batch_embed_messages(
            conversation_id=conversation_id,
            message_ids=message_ids,
            texts=texts,
        )

        return {
            "processed": len(results),
            "successful": sum(1 for v in results.values() if v),
            "failed": sum(1 for v in results.values() if not v),
            "results": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Batch processing failed",
        )
