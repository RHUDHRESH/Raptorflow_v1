"""CRUD operations for User model."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user(db: AsyncSession, user_id: UUID) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_auth_sub(db: AsyncSession, auth_sub: str) -> User | None:
    """Get user by external auth subject (Supabase UID)."""
    result = await db.execute(select(User).filter(User.auth_sub == auth_sub))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email."""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    auth_sub: str,
    email: str,
    display_name: str | None = None,
    avatar_url: str | None = None,
) -> User:
    """Create new user."""
    user = User(
        auth_sub=auth_sub,
        email=email,
        display_name=display_name or email.split("@")[0],
        avatar_url=avatar_url,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def create_user_from_jwt(db: AsyncSession, jwt_payload: dict[str, Any]) -> User:
    """
    Create user from JWT payload (first-time sign in).

    Args:
        db: Database session
        jwt_payload: Decoded JWT from Supabase

    Returns:
        Created user
    """
    user = await create_user(
        db,
        auth_sub=jwt_payload["sub"],
        email=jwt_payload.get("email"),
        display_name=jwt_payload.get("user_metadata", {}).get("full_name"),
        avatar_url=jwt_payload.get("user_metadata", {}).get("avatar_url"),
    )
    await db.commit()
    return user


async def update_user(
    db: AsyncSession,
    user_id: UUID,
    display_name: str | None = None,
    avatar_url: str | None = None,
) -> User | None:
    """Update user profile."""
    user = await get_user(db, user_id)
    if not user:
        return None

    if display_name is not None:
        user.display_name = display_name
    if avatar_url is not None:
        user.avatar_url = avatar_url

    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """Delete user (soft delete - anonymize data)."""
    user = await get_user(db, user_id)
    if not user:
        return False

    # Anonymize instead of delete (GDPR compliance)
    user.email = f"deleted_{user.id}@deleted.local"
    user.display_name = "Deleted User"
    user.avatar_url = None
    user.updated_at = datetime.utcnow()

    await db.commit()
    return True
