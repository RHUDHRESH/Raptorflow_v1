"""Organization endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, get_current_user_with_org, require_role
from app.crud.membership import create_membership, delete_membership, get_membership, update_membership_role
from app.crud.organization import (
    create_organization,
    delete_organization,
    get_organization,
    get_user_organizations,
    update_organization,
)
from app.db.session import get_db
from app.models.user import Organization, User, Membership
from app.schemas.auth import Principal, Role

router = APIRouter(prefix="/organizations", tags=["organizations"])


# ==========================================
# Request/Response Schemas
# ==========================================


class CreateOrganizationRequest(BaseModel):
    """Request to create organization."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")
    description: str | None = None


class UpdateOrganizationRequest(BaseModel):
    """Request to update organization."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    settings: dict | None = None


class OrganizationResponse(BaseModel):
    """Organization response."""

    id: UUID
    name: str
    slug: str
    description: str | None
    settings: dict
    created_at: str
    member_count: int | None = None
    current_user_role: Role | None = None

    class Config:
        from_attributes = True


class InviteMemberRequest(BaseModel):
    """Request to invite member to organization."""

    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    role: Role = Field(default=Role.VIEWER)


class UpdateMemberRoleRequest(BaseModel):
    """Request to update member role."""

    role: Role


class MemberResponse(BaseModel):
    """Member response."""

    user_id: UUID
    email: str
    display_name: str | None
    avatar_url: str | None
    role: Role
    joined_at: str
    invitation_status: str | None

    class Config:
        from_attributes = True


# ==========================================
# Organization CRUD Endpoints
# ==========================================


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all organizations the current user belongs to.

    Returns organizations with current user's role in each.
    """
    orgs = await get_user_organizations(db, user.id)

    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            description=org.description,
            settings=org.settings or {},
            created_at=org.created_at.isoformat(),
            current_user_role=next(
                (m.role for m in org.memberships if m.user_id == user.id), None
            ),
        )
        for org in orgs
    ]


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    request: CreateOrganizationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new organization.

    Current user becomes the owner.
    """
    # Check if slug is already taken
    result = await db.execute(select(Organization).filter(Organization.slug == request.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization with slug '{request.slug}' already exists",
        )

    # Create organization (will create owner membership)
    org = await create_organization(
        db,
        name=request.name,
        slug=request.slug,
        owner_id=user.id,
        description=request.description,
    )

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        settings=org.settings or {},
        created_at=org.created_at.isoformat(),
        current_user_role=Role.OWNER,
    )


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_org(
    org_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get organization details.

    User must be a member of the organization.
    """
    org = await get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check membership
    membership = await get_membership(db, user.id, org_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    # Count members
    member_count = len(org.memberships)

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        settings=org.settings or {},
        created_at=org.created_at.isoformat(),
        member_count=member_count,
        current_user_role=membership.role,
    )


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_org(
    org_id: UUID,
    request: UpdateOrganizationRequest,
    principal: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update organization details.

    Requires admin or owner role.
    """
    if principal.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")

    org = await update_organization(
        db,
        org_id=org_id,
        name=request.name,
        description=request.description,
        settings=request.settings,
    )

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        settings=org.settings or {},
        created_at=org.created_at.isoformat(),
        current_user_role=principal.role,
    )


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org(
    org_id: UUID,
    principal: Principal = Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete organization.

    Only owner can delete. This will cascade delete all related data.
    """
    if principal.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")

    success = await delete_organization(db, org_id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")

    return None


# ==========================================
# Member Management Endpoints
# ==========================================


@router.get("/{org_id}/members", response_model=List[MemberResponse])
async def list_members(
    org_id: UUID,
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    List all members of organization.

    All members can view the member list.
    """
    if principal.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")

    # Get organization with members
    result = await db.execute(
        select(Organization)
        .filter(Organization.id == org_id)
        .options(
            # Eager load memberships and users
            # Note: In production, use selectinload for better performance
        )
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Get all memberships with user data
    result = await db.execute(
        select(Membership, User)
        .join(User, Membership.user_id == User.id)
        .filter(Membership.org_id == org_id)
        .order_by(Membership.created_at)
    )
    memberships = result.all()

    return [
        MemberResponse(
            user_id=user.id,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            role=membership.role,
            joined_at=membership.created_at.isoformat(),
            invitation_status=membership.invitation_status,
        )
        for membership, user in memberships
    ]


@router.post("/{org_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: UUID,
    request: InviteMemberRequest,
    principal: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite user to organization.

    Requires admin or owner role.
    """
    if principal.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")

    # Find user by email
    result = await db.execute(select(User).filter(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with email '{request.email}' not found. They must sign up first.",
        )

    # Check if already a member
    existing = await get_membership(db, user.id, org_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="User is already a member of this organization",
        )

    # Create membership
    membership = await create_membership(
        db,
        org_id=org_id,
        user_id=user.id,
        role=request.role,
        invited_by=principal.user_id,
    )

    # TODO: Send invitation email

    return MemberResponse(
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=membership.role,
        joined_at=membership.created_at.isoformat(),
        invitation_status=membership.invitation_status,
    )


@router.patch("/{org_id}/members/{user_id}", response_model=MemberResponse)
async def update_member_role(
    org_id: UUID,
    user_id: UUID,
    request: UpdateMemberRoleRequest,
    principal: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update member's role.

    Requires admin or owner role. Cannot remove last owner.
    """
    if principal.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")

    # Cannot change own role
    if user_id == principal.user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot change your own role",
        )

    try:
        membership = await update_membership_role(db, user_id, org_id, request.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    # Get user details
    user = await db.get(User, user_id)

    return MemberResponse(
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=membership.role,
        joined_at=membership.created_at.isoformat(),
        invitation_status=membership.invitation_status,
    )


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: UUID,
    user_id: UUID,
    principal: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove member from organization.

    Requires admin or owner role. Cannot remove last owner.
    Members can remove themselves.
    """
    if principal.org_id != org_id:
        raise HTTPException(status_code=403, detail="Not authorized for this organization")

    # Allow users to remove themselves
    if user_id != principal.user_id:
        # Requires admin role to remove others
        if principal.role < Role.ADMIN:
            raise HTTPException(status_code=403, detail="Requires admin role to remove members")

    try:
        success = await delete_membership(db, user_id, org_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="Member not found")

    return None
