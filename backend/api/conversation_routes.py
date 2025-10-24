"""
Conversation API Routes
=======================

REST API endpoints for conversation management:
- Create, read, update, delete conversations
- Add and retrieve messages
- List conversations with pagination
- Search conversations

Authentication required: JWT token
"""

import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request, Query, Body
from pydantic import BaseModel, Field

from backend.utils.conversation_manager import (
    get_conversation_manager,
    Conversation,
    Message,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)


# ==================== Request/Response Models ====================

class CreateConversationRequest(BaseModel):
    """Create conversation request"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    agent_type: Optional[str] = Field(
        None,
        description="Type of agent: research, strategy, content, etc"
    )
    settings: Optional[Dict[str, Any]] = Field(
        default={},
        description="Model settings: temperature, top_k, etc"
    )


class ConversationResponse(BaseModel):
    """Conversation response model"""
    id: str
    org_id: str
    user_id: str
    title: str
    description: Optional[str]
    agent_type: Optional[str]
    status: str
    message_count: int
    token_count: int
    settings: Dict[str, Any]
    created_at: str
    updated_at: str


class AddMessageRequest(BaseModel):
    """Add message request"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = Field(
        default={},
        description="tokens, model, latency, etc"
    )


class MessageResponse(BaseModel):
    """Message response model"""
    id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    metadata: Dict[str, Any]
    created_at: str


class UpdateConversationRequest(BaseModel):
    """Update conversation request"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(
        None,
        description="active, archived, or deleted"
    )
    settings: Optional[Dict[str, Any]] = None


class ConversationListResponse(BaseModel):
    """List conversations response"""
    conversations: List[ConversationResponse]
    total: int
    limit: int
    offset: int


# ==================== Endpoints ====================

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: Request,
    payload: CreateConversationRequest,
) -> ConversationResponse:
    """
    Create a new conversation

    **Authentication**: Required (JWT token)

    **Request Body**:
    ```json
    {
      "title": "Marketing Strategy Q4",
      "description": "Quarterly strategy planning",
      "agent_type": "strategy",
      "settings": {"temperature": 0.7, "top_k": 5}
    }
    ```

    **Response**: Created conversation

    **Status Codes**:
    - 201: Conversation created
    - 401: Not authenticated
    - 400: Invalid request
    """
    try:
        # Get user from JWT (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
            )

        # Create conversation
        manager = get_conversation_manager()
        conversation = await manager.create_conversation(
            org_id=org_id,
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            agent_type=payload.agent_type,
            settings=payload.settings,
        )

        return ConversationResponse(**conversation.__dict__)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create conversation",
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    request: Request,
) -> ConversationResponse:
    """
    Get conversation details

    **Path Parameters**:
    - conversation_id: UUID

    **Response**: Conversation object

    **Status Codes**:
    - 200: Success
    - 401: Not authenticated
    - 404: Conversation not found
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        manager = get_conversation_manager()
        conversation = await manager.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            org_id=org_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        return ConversationResponse(**conversation.__dict__)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get conversation",
        )


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str = Query("active", description="Filter by status"),
) -> ConversationListResponse:
    """
    List conversations for current user

    **Query Parameters**:
    - limit: Max conversations (1-100, default 20)
    - offset: Pagination offset (default 0)
    - status: Filter by status (active, archived, deleted)

    **Response**: List of conversations with pagination

    **Status Codes**:
    - 200: Success
    - 401: Not authenticated
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        manager = get_conversation_manager()
        conversations = await manager.list_conversations(
            org_id=org_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
            status=status,
        )

        return ConversationListResponse(
            conversations=[
                ConversationResponse(**c.__dict__) for c in conversations
            ],
            total=len(conversations),
            limit=limit,
            offset=offset,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list conversations",
        )


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    request: Request,
    payload: AddMessageRequest,
) -> MessageResponse:
    """
    Add message to conversation

    **Path Parameters**:
    - conversation_id: UUID

    **Request Body**:
    ```json
    {
      "role": "user",
      "content": "What should our Q4 marketing focus be?",
      "metadata": {"tokens": 42, "model": "gpt-4"}
    }
    ```

    **Response**: Created message

    **Status Codes**:
    - 201: Message added
    - 401: Not authenticated
    - 404: Conversation not found
    - 400: Invalid request
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Validate role
        if payload.role not in ["user", "assistant"]:
            raise HTTPException(
                status_code=400,
                detail="Role must be 'user' or 'assistant'",
            )

        # Verify conversation exists and belongs to user
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            org_id=org_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        # Add message
        message = await manager.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=payload.role,
            content=payload.content,
            metadata=payload.metadata,
        )

        return MessageResponse(**message.__dict__)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add message: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to add message",
        )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> List[MessageResponse]:
    """
    Get conversation messages

    **Path Parameters**:
    - conversation_id: UUID

    **Query Parameters**:
    - limit: Max messages (1-200, default 50)
    - offset: Pagination offset

    **Response**: List of messages

    **Status Codes**:
    - 200: Success
    - 401: Not authenticated
    - 404: Conversation not found
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Verify conversation exists
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            org_id=org_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        # Get messages
        messages = await manager.get_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )

        return [MessageResponse(**m.__dict__) for m in messages]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get messages",
        )


@router.get("/{conversation_id}/messages/recent", response_model=List[MessageResponse])
async def get_recent_messages(
    conversation_id: str,
    request: Request,
    limit: int = Query(10, ge=1, le=50),
) -> List[MessageResponse]:
    """
    Get recent messages (for context window)

    **Path Parameters**:
    - conversation_id: UUID

    **Query Parameters**:
    - limit: Number of recent messages (1-50, default 10)

    **Response**: Most recent messages in chronological order

    **Status Codes**:
    - 200: Success
    - 401: Not authenticated
    - 404: Conversation not found
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Verify conversation exists
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            org_id=org_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        # Get recent messages
        messages = await manager.get_recent_messages(
            conversation_id=conversation_id,
            limit=limit,
        )

        return [MessageResponse(**m.__dict__) for m in messages]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recent messages: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get recent messages",
        )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: Request,
    payload: UpdateConversationRequest,
) -> ConversationResponse:
    """
    Update conversation metadata

    **Path Parameters**:
    - conversation_id: UUID

    **Request Body**:
    ```json
    {
      "title": "New title",
      "status": "archived",
      "settings": {"temperature": 0.8}
    }
    ```

    **Response**: Updated conversation

    **Status Codes**:
    - 200: Updated
    - 401: Not authenticated
    - 404: Conversation not found
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Build update dict (only include non-None fields)
        updates = {
            k: v for k, v in payload.__dict__.items()
            if v is not None
        }

        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No fields to update",
            )

        manager = get_conversation_manager()
        conversation = await manager.update_conversation(
            conversation_id=conversation_id,
            org_id=org_id,
            user_id=user_id,
            **updates,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        return ConversationResponse(**conversation.__dict__)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update conversation",
        )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    request: Request,
) -> Dict[str, str]:
    """
    Delete conversation (soft delete)

    **Path Parameters**:
    - conversation_id: UUID

    **Response**: Confirmation message

    **Status Codes**:
    - 200: Deleted
    - 401: Not authenticated
    - 404: Conversation not found
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        manager = get_conversation_manager()
        success = await manager.delete_conversation(
            conversation_id=conversation_id,
            org_id=org_id,
            user_id=user_id,
            soft_delete=True,
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        return {"message": "Conversation deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete conversation",
        )


@router.get("/search/by-title", response_model=List[ConversationResponse])
async def search_conversations(
    request: Request,
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
) -> List[ConversationResponse]:
    """
    Search conversations by title

    **Query Parameters**:
    - query: Search term (required)
    - limit: Max results (1-100, default 10)

    **Response**: List of matching conversations

    **Status Codes**:
    - 200: Success
    - 401: Not authenticated
    """
    try:
        org_id = getattr(request.state, "org_id", None)

        if not org_id:
            raise HTTPException(status_code=401, detail="Not authenticated")

        manager = get_conversation_manager()
        conversations = await manager.search_conversations(
            org_id=org_id,
            query=query,
            limit=limit,
        )

        return [ConversationResponse(**c.__dict__) for c in conversations]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search conversations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to search conversations",
        )
