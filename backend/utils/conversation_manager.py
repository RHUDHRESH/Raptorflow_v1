"""
Conversation Management Service
================================

Manages multi-turn conversations with AI agents:
- Create conversations
- Store messages (user + assistant)
- Retrieve conversation history
- Update conversation metadata
- Delete conversations

Integrates with:
- Supabase PostgreSQL database
- JWT authentication
- Organization scoping
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json

from backend.utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Single message in a conversation"""
    id: str
    conversation_id: str
    user_id: str
    role: str  # 'user' or 'assistant'
    content: str
    metadata: Dict[str, Any]  # tokens, model, latency, etc
    created_at: str


@dataclass
class Conversation:
    """Conversation metadata"""
    id: str
    org_id: str
    user_id: str
    title: str
    description: Optional[str]
    agent_type: Optional[str]  # 'research', 'strategy', 'content', etc
    status: str  # 'active', 'archived', 'deleted'
    message_count: int
    token_count: int
    settings: Dict[str, Any]  # model, temperature, top_k, etc
    created_at: str
    updated_at: str


class ConversationManager:
    """
    Manages conversation lifecycle and messages
    """

    def __init__(self):
        self.supabase = get_supabase_client()

    async def create_conversation(
        self,
        org_id: str,
        user_id: str,
        title: str,
        agent_type: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Conversation:
        """
        Create a new conversation

        Args:
            org_id: Organization ID
            user_id: User ID
            title: Conversation title
            agent_type: Type of agent (research, strategy, content, etc)
            description: Optional description
            settings: Model settings (temperature, top_k, etc)

        Returns:
            Created Conversation object

        Raises:
            ValueError: If creation fails
        """
        try:
            response = self.supabase.table("conversations").insert({
                "org_id": org_id,
                "user_id": user_id,
                "title": title,
                "description": description,
                "agent_type": agent_type,
                "status": "active",
                "message_count": 0,
                "token_count": 0,
                "settings": settings or {},
            }).execute()

            if not response.data:
                raise ValueError("Failed to create conversation")

            conv = response.data[0]
            logger.info(f"Created conversation: {conv['id']} for user {user_id}")

            return Conversation(
                id=conv["id"],
                org_id=conv["org_id"],
                user_id=conv["user_id"],
                title=conv["title"],
                description=conv.get("description"),
                agent_type=conv.get("agent_type"),
                status=conv["status"],
                message_count=conv["message_count"],
                token_count=conv["token_count"],
                settings=conv.get("settings", {}),
                created_at=conv["created_at"],
                updated_at=conv["updated_at"],
            )

        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise ValueError(f"Failed to create conversation: {e}")

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        org_id: str,
    ) -> Optional[Conversation]:
        """
        Get conversation details (with access check)

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for access control)
            org_id: Organization ID (for access control)

        Returns:
            Conversation object or None if not found/unauthorized
        """
        try:
            response = self.supabase.table("conversations").select(
                "*"
            ).eq("id", conversation_id).eq(
                "org_id", org_id
            ).eq("user_id", user_id).execute()

            if not response.data:
                logger.warning(
                    f"Conversation not found or unauthorized: {conversation_id}"
                )
                return None

            conv = response.data[0]
            return Conversation(
                id=conv["id"],
                org_id=conv["org_id"],
                user_id=conv["user_id"],
                title=conv["title"],
                description=conv.get("description"),
                agent_type=conv.get("agent_type"),
                status=conv["status"],
                message_count=conv["message_count"],
                token_count=conv["token_count"],
                settings=conv.get("settings", {}),
                created_at=conv["created_at"],
                updated_at=conv["updated_at"],
            )

        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None

    async def list_conversations(
        self,
        org_id: str,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: str = "active",
    ) -> List[Conversation]:
        """
        List conversations for user/org

        Args:
            org_id: Organization ID
            user_id: User ID
            limit: Max results
            offset: Pagination offset
            status: Filter by status (active, archived, deleted)

        Returns:
            List of Conversation objects
        """
        try:
            response = self.supabase.table("conversations").select(
                "*"
            ).eq("org_id", org_id).eq(
                "user_id", user_id
            ).eq("status", status).order(
                "created_at", desc=True
            ).range(offset, offset + limit - 1).execute()

            conversations = []
            for conv in response.data:
                conversations.append(Conversation(
                    id=conv["id"],
                    org_id=conv["org_id"],
                    user_id=conv["user_id"],
                    title=conv["title"],
                    description=conv.get("description"),
                    agent_type=conv.get("agent_type"),
                    status=conv["status"],
                    message_count=conv["message_count"],
                    token_count=conv["token_count"],
                    settings=conv.get("settings", {}),
                    created_at=conv["created_at"],
                    updated_at=conv["updated_at"],
                ))

            return conversations

        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []

    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,  # 'user' or 'assistant'
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """
        Add message to conversation

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (tokens, model, latency, etc)

        Returns:
            Created Message object

        Raises:
            ValueError: If message creation fails
        """
        try:
            response = self.supabase.table("conversation_messages").insert({
                "conversation_id": conversation_id,
                "user_id": user_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
            }).execute()

            if not response.data:
                raise ValueError("Failed to add message")

            msg = response.data[0]

            # Update conversation message count and token count
            token_count = metadata.get("tokens", 0) if metadata else 0
            await self._update_conversation_counts(
                conversation_id,
                token_count,
            )

            logger.info(
                f"Added {role} message to conversation {conversation_id}"
            )

            return Message(
                id=msg["id"],
                conversation_id=msg["conversation_id"],
                user_id=msg["user_id"],
                role=msg["role"],
                content=msg["content"],
                metadata=msg.get("metadata", {}),
                created_at=msg["created_at"],
            )

        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            raise ValueError(f"Failed to add message: {e}")

    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Message]:
        """
        Get conversation messages (sorted by created_at)

        Args:
            conversation_id: Conversation ID
            limit: Max messages to retrieve
            offset: Pagination offset

        Returns:
            List of Message objects
        """
        try:
            response = self.supabase.table("conversation_messages").select(
                "*"
            ).eq("conversation_id", conversation_id).order(
                "created_at", desc=False  # Oldest first
            ).range(offset, offset + limit - 1).execute()

            messages = []
            for msg in response.data:
                messages.append(Message(
                    id=msg["id"],
                    conversation_id=msg["conversation_id"],
                    user_id=msg["user_id"],
                    role=msg["role"],
                    content=msg["content"],
                    metadata=msg.get("metadata", {}),
                    created_at=msg["created_at"],
                ))

            return messages

        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    async def get_recent_messages(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> List[Message]:
        """
        Get recent messages (for context window)

        Args:
            conversation_id: Conversation ID
            limit: Number of recent messages

        Returns:
            List of Message objects (most recent first)
        """
        try:
            response = self.supabase.table("conversation_messages").select(
                "*"
            ).eq("conversation_id", conversation_id).order(
                "created_at", desc=True  # Newest first
            ).limit(limit).execute()

            messages = []
            for msg in response.data:
                messages.append(Message(
                    id=msg["id"],
                    conversation_id=msg["conversation_id"],
                    user_id=msg["user_id"],
                    role=msg["role"],
                    content=msg["content"],
                    metadata=msg.get("metadata", {}),
                    created_at=msg["created_at"],
                ))

            # Reverse to get chronological order
            return list(reversed(messages))

        except Exception as e:
            logger.error(f"Failed to get recent messages: {e}")
            return []

    async def update_conversation(
        self,
        conversation_id: str,
        org_id: str,
        user_id: str,
        **updates,
    ) -> Optional[Conversation]:
        """
        Update conversation metadata

        Args:
            conversation_id: Conversation ID
            org_id: Organization ID (for access control)
            user_id: User ID (for access control)
            **updates: Fields to update (title, status, settings, etc)

        Returns:
            Updated Conversation object
        """
        try:
            response = self.supabase.table("conversations").update(
                updates
            ).eq("id", conversation_id).eq(
                "org_id", org_id
            ).eq("user_id", user_id).execute()

            if not response.data:
                logger.warning(f"Conversation not found: {conversation_id}")
                return None

            conv = response.data[0]
            logger.info(f"Updated conversation: {conversation_id}")

            return Conversation(
                id=conv["id"],
                org_id=conv["org_id"],
                user_id=conv["user_id"],
                title=conv["title"],
                description=conv.get("description"),
                agent_type=conv.get("agent_type"),
                status=conv["status"],
                message_count=conv["message_count"],
                token_count=conv["token_count"],
                settings=conv.get("settings", {}),
                created_at=conv["created_at"],
                updated_at=conv["updated_at"],
            )

        except Exception as e:
            logger.error(f"Failed to update conversation: {e}")
            return None

    async def delete_conversation(
        self,
        conversation_id: str,
        org_id: str,
        user_id: str,
        soft_delete: bool = True,
    ) -> bool:
        """
        Delete conversation (soft or hard)

        Args:
            conversation_id: Conversation ID
            org_id: Organization ID (for access control)
            user_id: User ID (for access control)
            soft_delete: If True, set status='deleted'; if False, hard delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            if soft_delete:
                # Soft delete - mark as deleted
                response = self.supabase.table("conversations").update({
                    "status": "deleted"
                }).eq("id", conversation_id).eq(
                    "org_id", org_id
                ).eq("user_id", user_id).execute()
            else:
                # Hard delete - remove from database
                response = self.supabase.table("conversations").delete().eq(
                    "id", conversation_id
                ).eq("org_id", org_id).eq(
                    "user_id", user_id
                ).execute()

            logger.info(f"Deleted conversation: {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False

    async def search_conversations(
        self,
        org_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Conversation]:
        """
        Search conversations by title

        Args:
            org_id: Organization ID
            query: Search query
            limit: Max results

        Returns:
            List of matching Conversation objects
        """
        try:
            # Note: Supabase full-text search requires specific setup
            # This is a simple LIKE search
            response = self.supabase.table("conversations").select(
                "*"
            ).eq("org_id", org_id).ilike(
                "title", f"%{query}%"
            ).limit(limit).execute()

            conversations = []
            for conv in response.data:
                conversations.append(Conversation(
                    id=conv["id"],
                    org_id=conv["org_id"],
                    user_id=conv["user_id"],
                    title=conv["title"],
                    description=conv.get("description"),
                    agent_type=conv.get("agent_type"),
                    status=conv["status"],
                    message_count=conv["message_count"],
                    token_count=conv["token_count"],
                    settings=conv.get("settings", {}),
                    created_at=conv["created_at"],
                    updated_at=conv["updated_at"],
                ))

            return conversations

        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []

    async def _update_conversation_counts(
        self,
        conversation_id: str,
        token_count: int = 0,
    ) -> None:
        """
        Update conversation message and token counts

        Args:
            conversation_id: Conversation ID
            token_count: Tokens to add
        """
        try:
            # Get current counts
            response = self.supabase.table("conversations").select(
                "message_count, token_count"
            ).eq("id", conversation_id).execute()

            if not response.data:
                return

            current = response.data[0]
            new_message_count = current["message_count"] + 1
            new_token_count = current["token_count"] + token_count

            # Update counts
            self.supabase.table("conversations").update({
                "message_count": new_message_count,
                "token_count": new_token_count,
            }).eq("id", conversation_id).execute()

        except Exception as e:
            logger.error(f"Failed to update conversation counts: {e}")


# Singleton instance
_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """Get or create conversation manager instance"""
    global _manager
    if _manager is None:
        _manager = ConversationManager()
    return _manager
