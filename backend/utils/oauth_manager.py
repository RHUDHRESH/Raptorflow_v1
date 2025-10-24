"""
Google OAuth 2.0 Manager
========================

Handles Google OAuth authentication flow:
1. Generate authorization URL
2. Exchange code for tokens
3. Get user info from Google
4. Link/create user in Supabase
5. Generate JWT for RaptorFlow

Usage:
    manager = GoogleOAuthManager()
    auth_url = manager.get_authorization_url(state)
    user = await manager.handle_callback(code)
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

import httpx
import jwt
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token

logger = logging.getLogger(__name__)


@dataclass
class GoogleUser:
    """User info from Google OAuth"""
    sub: str
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False


@dataclass
class AuthToken:
    """JWT token response"""
    access_token: str
    refresh_token: Optional[str]
    expires_in: int
    token_type: str = "Bearer"


class GoogleOAuthManager:
    """
    Manages Google OAuth 2.0 flow and token exchange
    """

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/auth/google/callback"
        )
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm = "HS256"

        # Validate configuration
        if not all([self.client_id, self.client_secret, self.jwt_secret]):
            logger.warning("Google OAuth not fully configured")

        # Google OAuth endpoints
        self.authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Google OAuth authorization URL

        Args:
            state: CSRF protection token (should be random and stored in session)

        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",  # Request refresh token
            "prompt": "consent",  # Force consent screen to get refresh token
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.authorization_base_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token, refresh_token, expires_in
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data={
                        "code": code,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                        "grant_type": "authorization_code",
                    },
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"Token exchange failed: {e}")
                raise ValueError(f"Failed to exchange code for token: {e}")

    async def get_user_info(self, access_token: str) -> GoogleUser:
        """
        Get user info from Google using access token

        Args:
            access_token: Google access token

        Returns:
            GoogleUser with email, name, picture, etc.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                data = response.json()

                return GoogleUser(
                    sub=data.get("sub"),
                    email=data.get("email"),
                    name=data.get("name"),
                    picture=data.get("picture"),
                    email_verified=data.get("email_verified", False),
                )

            except httpx.HTTPError as e:
                logger.error(f"Failed to get user info: {e}")
                raise ValueError(f"Failed to get user info: {e}")

    async def verify_id_token(self, id_token: str) -> GoogleUser:
        """
        Verify Google ID token (alternative to access token)

        Args:
            id_token: ID token from OAuth response

        Returns:
            GoogleUser if token is valid

        Raises:
            ValueError: If token is invalid
        """
        try:
            # Verify token signature with Google's public keys
            request = Request()
            payload = verify_oauth2_token(id_token, request, self.client_id)

            return GoogleUser(
                sub=payload.get("sub"),
                email=payload.get("email"),
                name=payload.get("name"),
                picture=payload.get("picture"),
                email_verified=payload.get("email_verified", False),
            )

        except Exception as e:
            logger.error(f"ID token verification failed: {e}")
            raise ValueError(f"Invalid ID token: {e}")

    def generate_jwt(
        self,
        user_id: str,
        org_id: str,
        email: str,
        expires_in_hours: int = 24,
    ) -> AuthToken:
        """
        Generate JWT token for RaptorFlow

        Args:
            user_id: User UUID
            org_id: Organization UUID
            email: User email
            expires_in_hours: Token expiration time

        Returns:
            AuthToken with JWT access token
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=expires_in_hours)

        payload = {
            "sub": user_id,
            "org_id": org_id,
            "email": email,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "type": "access",
        }

        access_token = jwt.encode(
            payload,
            self.jwt_secret,
            algorithm=self.jwt_algorithm,
        )

        return AuthToken(
            access_token=access_token,
            refresh_token=None,  # Use refresh tokens separately if needed
            expires_in=expires_in_hours * 3600,
        )

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token to verify

        Returns:
            Decoded payload

        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm],
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")

    async def handle_oauth_callback(
        self,
        code: str,
        supabase_client,
    ) -> Dict[str, Any]:
        """
        Complete OAuth flow: code → token → user info → DB → JWT

        Args:
            code: Authorization code from OAuth callback
            supabase_client: Supabase client for user operations

        Returns:
            {
                "user": user_data,
                "org": org_data,
                "token": jwt_token,
                "is_new_user": bool
            }
        """
        try:
            # 1. Exchange code for tokens
            token_response = await self.exchange_code_for_token(code)
            access_token = token_response.get("access_token")

            # 2. Get user info from Google
            google_user = await self.get_user_info(access_token)
            logger.info(f"Google user authenticated: {google_user.email}")

            # 3. Link/create user in Supabase
            from backend.utils.supabase_client import get_supabase_client

            supabase = supabase_client or get_supabase_client()

            # Check if user already exists
            user_response = supabase.table("users").select("*").eq(
                "email", google_user.email
            ).execute()

            if user_response.data:
                # Existing user
                user = user_response.data[0]
                is_new_user = False
                logger.info(f"Existing user logged in: {user['id']}")

            else:
                # New user - create in users table
                user_response = supabase.table("users").insert({
                    "auth_sub": google_user.sub,
                    "email": google_user.email,
                    "display_name": google_user.name,
                    "avatar_url": google_user.picture,
                }).execute()

                user = user_response.data[0]
                is_new_user = True
                logger.info(f"New user created: {user['id']}")

            # 4. Get user's organization
            membership_response = supabase.table("memberships").select(
                "org_id, organizations(id, name, slug)"
            ).eq("user_id", user["id"]).execute()

            org = None
            if membership_response.data:
                org = membership_response.data[0]["organizations"]
            else:
                # New user - create default organization
                if is_new_user:
                    org_response = supabase.table("organizations").insert({
                        "name": f"{google_user.name}'s Organization",
                        "slug": google_user.email.split("@")[0],
                        "billing_email": google_user.email,
                    }).execute()

                    org = org_response.data[0]

                    # Add user as owner
                    supabase.table("memberships").insert({
                        "org_id": org["id"],
                        "user_id": user["id"],
                        "role": "owner",
                    }).execute()

                    logger.info(f"Default organization created: {org['id']}")

            # 5. Generate JWT
            jwt_token = self.generate_jwt(
                user_id=user["id"],
                org_id=org["id"] if org else None,
                email=user["email"],
            )

            return {
                "user": user,
                "org": org,
                "token": jwt_token,
                "is_new_user": is_new_user,
            }

        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            raise


# Singleton instance
_oauth_manager: Optional[GoogleOAuthManager] = None


def get_oauth_manager() -> GoogleOAuthManager:
    """Get or create OAuth manager instance"""
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = GoogleOAuthManager()
    return _oauth_manager
