"""User and profile endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, get_current_user_with_org
from app.crud.user import update_user, delete_user
from app.db.session import get_db
from app.models.user import User, Membership, Organization
from app.schemas.auth import Principal, Role

router = APIRouter(prefix="/users", tags=["users"])


# ==========================================
# Request/Response Schemas
# ==========================================


class UpdateProfileRequest(BaseModel):
    """Request to update user profile."""

    display_name: str | None = Field(None, min_length=1, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)
    bio: str | None = Field(None, max_length=500)
    settings: dict | None = None


class UserProfileResponse(BaseModel):
    """User profile response."""

    id: UUID
    email: str
    display_name: str | None
    avatar_url: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UserOrganizationResponse(BaseModel):
    """User's organization membership."""

    org_id: UUID
    org_name: str
    org_slug: str
    role: Role
    joined_at: str
    invitation_status: str | None

    class Config:
        from_attributes = True


class UserActivityResponse(BaseModel):
    """User activity summary."""

    total_organizations: int
    total_projects_created: int
    total_indicators_created: int
    recent_logins: List[str]
    last_active_at: str | None


class APIKeyResponse(BaseModel):
    """API key response."""

    id: UUID
    name: str
    prefix: str  # First 8 chars of key for identification
    created_at: str
    expires_at: str | None
    last_used_at: str | None
    scopes: List[str]


class CreateAPIKeyRequest(BaseModel):
    """Request to create API key."""

    name: str = Field(..., min_length=1, max_length=100)
    expires_days: int | None = Field(None, ge=1, le=365)
    scopes: List[str] = Field(default_factory=lambda: ["read"])


class CreateAPIKeyResponse(BaseModel):
    """Response with new API key (shown only once)."""

    id: UUID
    name: str
    key: str  # Full key - only shown once!
    prefix: str
    created_at: str
    expires_at: str | None


# ==========================================
# Profile Endpoints
# ==========================================


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    user: User = Depends(get_current_user),
):
    """
    Get current user's profile.

    No organization context required.
    """
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )


@router.patch("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    request: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile.

    Users can only update their own profile.
    """
    updated_user = await update_user(
        db,
        user_id=user.id,
        display_name=request.display_name,
        avatar_url=request.avatar_url,
        settings=request.settings,
    )

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfileResponse(
        id=updated_user.id,
        email=updated_user.email,
        display_name=updated_user.display_name,
        avatar_url=updated_user.avatar_url,
        created_at=updated_user.created_at.isoformat(),
        updated_at=updated_user.updated_at.isoformat(),
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user_account(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete current user's account.

    This will anonymize user data for GDPR compliance.
    User must not be the last owner of any organization.
    """
    # Check if user is the last owner of any organization
    result = await db.execute(
        select(Membership, Organization)
        .join(Organization, Membership.org_id == Organization.id)
        .filter(
            Membership.user_id == user.id,
            Membership.role == Role.OWNER,
        )
    )
    memberships = result.all()

    for membership, org in memberships:
        # Count owners in this org
        owner_result = await db.execute(
            select(Membership).filter(
                Membership.org_id == org.id,
                Membership.role == Role.OWNER,
            )
        )
        owner_count = len(list(owner_result.scalars().all()))

        if owner_count <= 1:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete account. You are the last owner of organization '{org.name}'. "
                f"Transfer ownership or delete the organization first.",
            )

    # Anonymize user (GDPR-compliant deletion)
    success = await delete_user(db, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return None


@router.get("/me/organizations", response_model=List[UserOrganizationResponse])
async def get_user_organizations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all organizations the current user belongs to.

    Returns organizations with user's role in each.
    """
    result = await db.execute(
        select(Membership, Organization)
        .join(Organization, Membership.org_id == Organization.id)
        .filter(Membership.user_id == user.id)
        .order_by(Membership.created_at.desc())
    )
    memberships = result.all()

    return [
        UserOrganizationResponse(
            org_id=org.id,
            org_name=org.name,
            org_slug=org.slug,
            role=membership.role,
            joined_at=membership.created_at.isoformat(),
            invitation_status=membership.invitation_status,
        )
        for membership, org in memberships
    ]


@router.get("/me/activity", response_model=UserActivityResponse)
async def get_user_activity(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's activity summary.

    Returns counts and recent activity.
    """
    # Count organizations
    result = await db.execute(
        select(Membership).filter(Membership.user_id == user.id)
    )
    org_count = len(list(result.scalars().all()))

    # TODO: Count projects, indicators when models are created
    # For now, return mock data

    return UserActivityResponse(
        total_organizations=org_count,
        total_projects_created=0,
        total_indicators_created=0,
        recent_logins=[],
        last_active_at=user.updated_at.isoformat(),
    )


# ==========================================
# API Key Management
# ==========================================


@router.get("/me/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    List API keys for current organization.

    API keys are scoped to organization, not user.
    """
    # TODO: Implement when APIKey model is created
    # For now, return empty list
    return []


@router.post("/me/api-keys", response_model=CreateAPIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: CreateAPIKeyRequest,
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new API key for organization.

    The full key is only shown once! Save it securely.
    Requires current organization context (X-Organization-ID header).
    """
    # TODO: Implement when APIKey model is created
    # For now, return mock response
    from datetime import datetime, timedelta
    from uuid import uuid4
    import secrets

    # Generate API key
    key = f"rk_{secrets.token_urlsafe(32)}"
    prefix = key[:11]  # rk_ + first 8 chars

    raise HTTPException(
        status_code=501,
        detail="API key management not yet implemented. See app/models/user.py for APIKey model TODO",
    )


@router.delete("/me/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: UUID,
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke API key.

    Key will be immediately invalidated and cannot be restored.
    """
    # TODO: Implement when APIKey model is created
    raise HTTPException(
        status_code=501,
        detail="API key management not yet implemented. See app/models/user.py for APIKey model TODO",
    )


# ==========================================
# Admin Endpoints (Organization-Scoped)
# ==========================================


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_by_id(
    user_id: UUID,
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user profile by ID.

    User must be in the same organization as the requesting user.
    """
    # Verify target user is in same organization
    result = await db.execute(
        select(Membership).filter(
            Membership.user_id == user_id,
            Membership.org_id == principal.org_id,
        )
    )
    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=404,
            detail="User not found in this organization",
        )

    # Get user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )
