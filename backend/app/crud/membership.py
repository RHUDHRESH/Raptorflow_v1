"""CRUD operations for Membership model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Membership, Role, User


async def get_membership(
    db: AsyncSession,
    user_id: UUID,
    org_id: UUID,
) -> Membership | None:
    """Get membership for user in organization."""
    result = await db.execute(
        select(Membership).filter(
            Membership.user_id == user_id,
            Membership.org_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def get_org_members(db: AsyncSession, org_id: UUID) -> list[Membership]:
    """Get all members of organization."""
    result = await db.execute(
        select(Membership)
        .filter(Membership.org_id == org_id)
        .order_by(Membership.role.desc(), Membership.created_at.asc())
    )
    return list(result.scalars().all())


async def create_membership(
    db: AsyncSession,
    org_id: UUID,
    user_id: UUID,
    role: Role,
    invited_by: UUID | None = None,
) -> Membership:
    """
    Create new membership (invite user to org).

    Args:
        db: Database session
        org_id: Organization ID
        user_id: User ID to invite
        role: Role to assign
        invited_by: User ID who sent the invite

    Returns:
        Created membership
    """
    membership = Membership(
        org_id=org_id,
        user_id=user_id,
        role=role,
        invited_by=invited_by,
        invited_at=datetime.utcnow(),
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def accept_membership(
    db: AsyncSession,
    user_id: UUID,
    org_id: UUID,
) -> Membership | None:
    """Accept organization invitation."""
    membership = await get_membership(db, user_id, org_id)
    if not membership:
        return None

    membership.accepted_at = datetime.utcnow()
    await db.commit()
    await db.refresh(membership)
    return membership


async def update_membership_role(
    db: AsyncSession,
    user_id: UUID,
    org_id: UUID,
    new_role: Role,
) -> Membership | None:
    """Update user's role in organization."""
    membership = await get_membership(db, user_id, org_id)
    if not membership:
        return None

    # Don't allow changing last owner to non-owner
    if membership.role == Role.OWNER and new_role != Role.OWNER:
        owner_count = await db.execute(
            select(Membership).filter(
                Membership.org_id == org_id,
                Membership.role == Role.OWNER,
            )
        )
        if len(list(owner_count.scalars().all())) <= 1:
            raise ValueError("Organization must have at least one owner")

    membership.role = new_role
    await db.commit()
    await db.refresh(membership)
    return membership


async def delete_membership(
    db: AsyncSession,
    user_id: UUID,
    org_id: UUID,
) -> bool:
    """
    Remove user from organization.

    Raises:
        ValueError: If trying to remove last owner
    """
    membership = await get_membership(db, user_id, org_id)
    if not membership:
        return False

    # Don't allow removing last owner
    if membership.role == Role.OWNER:
        owner_count = await db.execute(
            select(Membership).filter(
                Membership.org_id == org_id,
                Membership.role == Role.OWNER,
            )
        )
        if len(list(owner_count.scalars().all())) <= 1:
            raise ValueError("Cannot remove last owner from organization")

    await db.delete(membership)
    await db.commit()
    return True
