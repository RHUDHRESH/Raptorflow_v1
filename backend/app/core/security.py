"""Security utilities for authentication and authorization."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any

import httpx
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, Membership, APIKey
from app.schemas.auth import Principal

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_scheme = HTTPBearer(scheme_name="API Key", auto_error=False)


async def verify_jwt_token(token: str) -> dict[str, Any]:
    """
    Verify JWT token from Supabase.

    Args:
        token: JWT access token

    Returns:
        Decoded JWT payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Dependency that validates JWT and loads user from database.
    Creates user on first sign-in.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify JWT
    payload = await verify_jwt_token(credentials.credentials)

    # Extract user info
    auth_sub = payload.get("sub")
    email = payload.get("email")

    if not auth_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )

    # Get or create user
    from app.crud.user import get_user_by_auth_sub, create_user_from_jwt

    user = await get_user_by_auth_sub(db, auth_sub)
    if not user:
        # First-time sign in - create user
        user = await create_user_from_jwt(db, payload)

    return user


async def get_current_user_with_org(
    user: User = Depends(get_current_user),
    x_organization_id: str = Header(None, alias="X-Organization-ID"),
    db: AsyncSession = Depends(get_db),
) -> Principal:
    """
    Get current user with organization context.

    Loads user's membership in the specified organization.

    Args:
        user: Current authenticated user
        x_organization_id: Organization ID from header
        db: Database session

    Returns:
        Principal with user, org, and role

    Raises:
        HTTPException: If user not member of org
    """
    if not x_organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Organization-ID header required",
        )

    # Load membership
    from app.crud.membership import get_membership

    membership = await get_membership(db, user.id, x_organization_id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )

    return Principal(
        user=user,
        org_id=membership.org_id,
        role=membership.role,
    )


def require_role(min_role: str):
    """
    Dependency factory to enforce minimum role requirement.

    Usage:
        @router.post("/projects", dependencies=[Depends(require_role("editor"))])
        async def create_project(...):
            ...

    Args:
        min_role: Minimum required role (viewer, editor, admin, owner)

    Returns:
        Dependency function
    """
    from app.models.user import Role

    role_map = {
        "viewer": Role.VIEWER,
        "editor": Role.EDITOR,
        "admin": Role.ADMIN,
        "owner": Role.OWNER,
    }

    required_role = role_map.get(min_role.lower())
    if not required_role:
        raise ValueError(f"Invalid role: {min_role}")

    async def check_role(principal: Principal = Depends(get_current_user_with_org)):
        if principal.role.value < required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {min_role} role or higher",
            )
        return principal

    return check_role


async def verify_api_key(
    x_api_key: str = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """
    Verify API key authentication.

    Alternative to JWT for programmatic access.

    Args:
        x_api_key: API key from header
        db: Database session

    Returns:
        APIKey object

    Raises:
        HTTPException: If API key invalid or revoked
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header required",
        )

    # Validate format
    if not x_api_key.startswith("rk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
        )

    # Hash key for lookup
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()

    # Load from database
    from app.crud.api_key import get_api_key_by_hash

    api_key = await get_api_key_by_hash(db, key_hash)
    if not api_key or api_key.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )

    # Check expiration
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired",
        )

    # Update last used
    api_key.last_used_at = datetime.utcnow()
    await db.commit()

    return api_key


def create_api_key(org_id: str, name: str, scopes: list[str]) -> tuple[str, dict]:
    """
    Generate new API key.

    Args:
        org_id: Organization ID
        name: Human-readable name
        scopes: List of permission scopes

    Returns:
        Tuple of (raw_key, key_data)

    Note:
        Raw key is only returned ONCE. Store securely!
    """
    # Generate random key
    raw_key = f"rk_{secrets.token_urlsafe(32)}"

    # Hash for storage
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12]  # "rk_xxxxxxxx"

    key_data = {
        "org_id": org_id,
        "name": name,
        "key_prefix": key_prefix,
        "key_hash": key_hash,
        "scopes": scopes,
    }

    return raw_key, key_data


def hash_password(password: str) -> str:
    """Hash password using SHA-256 (for API keys, not user passwords)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_razorpay_signature(body: bytes, signature: str) -> bool:
    """
    Verify Razorpay webhook signature.

    Args:
        body: Request body (raw bytes)
        signature: X-Razorpay-Signature header

    Returns:
        True if valid, False otherwise
    """
    import hmac

    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
