"""Authentication and authorization schemas."""

from datetime import datetime
from enum import IntEnum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Role(IntEnum):
    """User role hierarchy (higher value = more permissions)."""

    VIEWER = 1
    EDITOR = 2
    ADMIN = 3
    OWNER = 4


class Principal(BaseModel):
    """
    Authenticated principal with org context.

    Represents the current user in the context of an organization.
    Used throughout the app to enforce permissions.
    """

    user_id: UUID
    org_id: UUID
    role: Role
    email: str
    display_name: str | None = None

    # Convenience fields
    user: Any | None = Field(None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def can(self, action: str, resource: str | None = None) -> bool:
        """
        Check if principal has permission for action.

        Args:
            action: Action to check (e.g., "create_project")
            resource: Optional resource type

        Returns:
            True if allowed, False otherwise
        """
        # Permission matrix
        permissions = {
            # Organizations
            "view_org": Role.VIEWER,
            "edit_org": Role.OWNER,
            "delete_org": Role.OWNER,
            # Members
            "view_members": Role.VIEWER,
            "invite_member": Role.ADMIN,
            "remove_member": Role.ADMIN,
            "change_role": Role.ADMIN,
            # Projects
            "view_project": Role.VIEWER,
            "create_project": Role.EDITOR,
            "edit_project": Role.EDITOR,
            "delete_project": Role.ADMIN,
            # Agents
            "run_agent": Role.EDITOR,
            "configure_agent": Role.EDITOR,
            "view_results": Role.VIEWER,
            # Billing
            "view_billing": Role.OWNER,
            "manage_subscription": Role.OWNER,
            # API Keys
            "view_api_keys": Role.ADMIN,
            "create_api_key": Role.ADMIN,
            "revoke_api_key": Role.ADMIN,
        }

        required_role = permissions.get(action, Role.OWNER)
        return self.role >= required_role

    @property
    def is_owner(self) -> bool:
        """Check if user is owner."""
        return self.role == Role.OWNER

    @property
    def is_admin(self) -> bool:
        """Check if user is admin or higher."""
        return self.role >= Role.ADMIN

    @property
    def is_editor(self) -> bool:
        """Check if user is editor or higher."""
        return self.role >= Role.EDITOR


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # Subject (user ID)
    email: EmailStr
    exp: int  # Expiration timestamp
    iat: int  # Issued at
    aud: str = "authenticated"


class APIKeyCreate(BaseModel):
    """Request to create API key."""

    name: str = Field(..., min_length=1, max_length=100)
    scopes: list[str] = Field(default_factory=list)
    expires_days: int | None = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """API key creation response (includes raw key ONCE)."""

    id: UUID
    name: str
    key: str  # Raw key (only shown once!)
    key_prefix: str
    scopes: list[str]
    expires_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyList(BaseModel):
    """API key list item (no raw key)."""

    id: UUID
    name: str
    key_prefix: str
    scopes: list[str]
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked: bool
    created_at: datetime

    class Config:
        from_attributes = True
