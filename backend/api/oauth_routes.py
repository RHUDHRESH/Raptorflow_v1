"""
OAuth Authentication Routes
=============================

Endpoints for Google OAuth 2.0 authentication flow:
- GET /login - Initiate OAuth flow
- GET /callback - Handle OAuth callback
- POST /logout - Logout user
- POST /refresh - Refresh token
"""

import os
import secrets
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response, Query
from pydantic import BaseModel

from backend.utils.oauth_manager import get_oauth_manager
from backend.utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


# Request/Response Models
class LoginResponse(BaseModel):
    """Response for login initiation"""
    authorization_url: str
    state: str


class CallbackRequest(BaseModel):
    """OAuth callback request"""
    code: str
    state: Optional[str] = None


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: dict
    org: dict
    is_new_user: bool


class LogoutRequest(BaseModel):
    """Logout request"""
    pass


class RefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


@router.get("/google/login")
async def google_login(request: Request) -> LoginResponse:
    """
    Initiate Google OAuth flow

    Returns authorization URL to redirect user to Google login.

    Query Parameters:
        redirect_after_login: URL to redirect to after login (optional)

    Returns:
        {
            "authorization_url": "https://accounts.google.com/...",
            "state": "random-state-token"
        }
    """
    try:
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state in session (in production, use secure session store)
        if not hasattr(request.state, "oauth_state"):
            request.state.oauth_state = {}
        request.state.oauth_state[state] = {
            "created_at": str(__import__("datetime").datetime.utcnow()),
        }

        # Get OAuth manager
        oauth_manager = get_oauth_manager()

        # Generate authorization URL
        auth_url = oauth_manager.get_authorization_url(state)

        logger.info(f"OAuth login initiated with state: {state}")

        return LoginResponse(
            authorization_url=auth_url,
            state=state,
        )

    except Exception as e:
        logger.error(f"Failed to initiate OAuth login: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initiate login",
        )


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: Optional[str] = Query(None, description="State token for CSRF protection"),
    request: Request = None,
) -> TokenResponse:
    """
    Handle Google OAuth callback

    Called by Google after user authorization. Exchanges code for tokens
    and creates/links user in database.

    Query Parameters:
        code: Authorization code from Google (required)
        state: State token for CSRF protection (optional)

    Returns:
        {
            "access_token": "eyJ0eXAiOiJKV1Q...",
            "token_type": "Bearer",
            "expires_in": 86400,
            "user": {...},
            "org": {...},
            "is_new_user": true/false
        }
    """
    try:
        # Validate state token (CSRF protection)
        if state and hasattr(request.state, "oauth_state"):
            if state not in request.state.oauth_state:
                logger.warning(f"Invalid state token: {state}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid state token - potential CSRF attack",
                )

        # Get OAuth manager
        oauth_manager = get_oauth_manager()

        # Get Supabase client
        supabase = get_supabase_client()

        # Complete OAuth flow
        result = await oauth_manager.handle_oauth_callback(code, supabase)

        logger.info(
            f"OAuth callback successful for user: {result['user']['email']}"
        )

        return TokenResponse(
            access_token=result["token"].access_token,
            token_type="Bearer",
            expires_in=result["token"].expires_in,
            user=result["user"],
            org=result["org"],
            is_new_user=result["is_new_user"],
        )

    except ValueError as e:
        logger.error(f"OAuth callback validation failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication failed",
        )


@router.post("/logout")
async def logout(request: Request) -> dict:
    """
    Logout user by invalidating tokens

    In practice, this is handled by deleting the token on the client side.
    Server-side logout would require token blacklisting (Redis, etc.).

    Returns:
        {"message": "Logged out successfully"}
    """
    try:
        # Get user from request (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        if user_id:
            logger.info(f"User logged out: {user_id}")
        else:
            logger.warning("Logout attempted without authenticated user")

        return {"message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Logout failed",
        )


@router.post("/refresh")
async def refresh_token(request: RefreshRequest) -> TokenResponse:
    """
    Refresh authentication token

    Uses a refresh token to get a new access token without re-authenticating.

    Request Body:
        {
            "refresh_token": "refresh-token-value"
        }

    Returns:
        New access token
    """
    try:
        # In a production system, you would:
        # 1. Validate the refresh token
        # 2. Check if it's expired or blacklisted
        # 3. Issue a new access token
        # 4. Optionally issue a new refresh token

        logger.warning("Token refresh endpoint called but not fully implemented")

        raise HTTPException(
            status_code=501,
            detail="Refresh token flow not yet implemented",
        )

    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh token",
        )


@router.get("/me")
async def get_current_user(request: Request) -> dict:
    """
    Get current authenticated user

    Returns user information from the JWT token.

    Returns:
        {
            "user_id": "uuid",
            "email": "user@example.com",
            "org_id": "uuid",
            "token_type": "Bearer"
        }
    """
    try:
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "org_id", None)

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
            )

        # Get user from database
        supabase = get_supabase_client()
        user_response = supabase.table("users").select("*").eq(
            "id", user_id
        ).execute()

        if not user_response.data:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        user = user_response.data[0]

        return {
            "user_id": user["id"],
            "email": user["email"],
            "display_name": user.get("display_name"),
            "avatar_url": user.get("avatar_url"),
            "org_id": org_id,
            "created_at": user.get("created_at"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get user information",
        )


@router.post("/verify-token")
async def verify_token(request: Request) -> dict:
    """
    Verify if current JWT token is valid

    Returns:
        {
            "valid": true,
            "user_id": "uuid",
            "org_id": "uuid",
            "expires_in": 86400
        }
    """
    try:
        user_id = getattr(request.state, "user_id", None)

        if not user_id:
            return {"valid": False}

        return {
            "valid": True,
            "user_id": user_id,
            "org_id": getattr(request.state, "org_id", None),
            "message": "Token is valid",
        }

    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return {"valid": False}
