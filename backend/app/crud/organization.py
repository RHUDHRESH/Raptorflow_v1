"""CRUD operations for Organization model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Organization, Membership, Role


async def get_organization(db: AsyncSession, org_id: UUID) -> Organization | None:
    """Get organization by ID."""
    result = await db.execute(select(Organization).filter(Organization.id == org_id))
    return result.scalar_one_or_none()


async def get_organization_by_slug(db: AsyncSession, slug: str) -> Organization | None:
    """Get organization by slug."""
    result = await db.execute(select(Organization).filter(Organization.slug == slug))
    return result.scalar_one_or_none()


async def create_organization(
    db: AsyncSession,
    name: str,
    slug: str,
    owner_id: UUID,
    billing_email: str | None = None,
) -> Organization:
    """
    Create new organization with owner.

    Args:
        db: Database session
        name: Organization name
        slug: URL-friendly identifier
        owner_id: User ID who will be the owner
        billing_email: Optional billing email

    Returns:
        Created organization
    """
    # Create organization
    org = Organization(
        name=name,
        slug=slug,
        billing_email=billing_email,
        settings={},
    )
    db.add(org)
    await db.flush()

    # Create owner membership
    membership = Membership(
        org_id=org.id,
        user_id=owner_id,
        role=Role.OWNER,
        accepted_at=datetime.utcnow(),
    )
    db.add(membership)

    await db.commit()
    await db.refresh(org)
    return org


async def update_organization(
    db: AsyncSession,
    org_id: UUID,
    name: str | None = None,
    billing_email: str | None = None,
    website: str | None = None,
    industry: str | None = None,
    size: str | None = None,
    logo_url: str | None = None,
    settings: dict | None = None,
) -> Organization | None:
    """Update organization."""
    org = await get_organization(db, org_id)
    if not org:
        return None

    if name is not None:
        org.name = name
    if billing_email is not None:
        org.billing_email = billing_email
    if website is not None:
        org.website = website
    if industry is not None:
        org.industry = industry
    if size is not None:
        org.size = size
    if logo_url is not None:
        org.logo_url = logo_url
    if settings is not None:
        org.settings = settings

    org.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(org)
    return org


async def delete_organization(db: AsyncSession, org_id: UUID) -> bool:
    """
    Delete organization.

    Note: This cascades to all related data (memberships, projects, etc.)
    """
    org = await get_organization(db, org_id)
    if not org:
        return False

    await db.delete(org)
    await db.commit()
    return True


async def get_user_organizations(db: AsyncSession, user_id: UUID) -> list[Organization]:
    """Get all organizations user is a member of."""
    result = await db.execute(
        select(Organization)
        .join(Membership)
        .filter(Membership.user_id == user_id)
        .order_by(Organization.created_at.desc())
    )
    return list(result.scalars().all())
