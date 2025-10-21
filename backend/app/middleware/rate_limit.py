"""Rate limiting middleware using Redis."""

import time
from typing import Callable

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger
from app.core.redis import redis_client

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.

    Limits requests per organization based on subscription plan.
    Uses Redis for distributed rate limiting.
    """

    # Default rate limits (requests per minute)
    DEFAULT_LIMITS = {
        "free": 100,  # 100 requests/minute
        "pro": 1000,  # 1000 requests/minute
        "enterprise": 10000,  # 10000 requests/minute
    }

    async def dispatch(self, request: Request, call_next: Callable):
        """Apply rate limiting."""
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limit(request):
            return await call_next(request)

        # Get organization ID
        org_id = request.headers.get("X-Organization-ID")
        if not org_id:
            # No org context - use IP-based rate limiting
            identifier = request.client.host if request.client else "unknown"
            limit = 60  # 60 requests/minute for unauthenticated requests
        else:
            identifier = f"org:{org_id}"
            # TODO: Get plan from database
            # For now, use pro tier limits
            limit = self.DEFAULT_LIMITS["pro"]

        # Check rate limit
        allowed, current, reset_time = await self._check_rate_limit(
            identifier, limit, window=60
        )

        # Add rate limit headers
        response = None
        if allowed:
            response = await call_next(request)
        else:
            # Rate limit exceeded
            logger.warning(
                "rate_limit_exceeded",
                identifier=identifier,
                limit=limit,
                current=current,
                reset_time=reset_time,
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Try again in {reset_time} seconds.",
                        "limit": limit,
                        "current": current,
                        "reset_time": reset_time,
                    }
                },
            )

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + reset_time))

        return response

    @staticmethod
    def _should_skip_rate_limit(request: Request) -> bool:
        """Check if request should skip rate limiting."""
        # Skip rate limiting for health checks and webhooks
        skip_paths = {"/health", "/health/db", "/health/redis", "/api/v1/payments/webhooks"}
        return request.url.path in skip_paths

    @staticmethod
    async def _check_rate_limit(
        identifier: str, limit: int, window: int = 60
    ) -> tuple[bool, int, int]:
        """
        Check rate limit using sliding window algorithm.

        Args:
            identifier: Unique identifier (org ID, IP, etc.)
            limit: Maximum requests allowed in window
            window: Time window in seconds

        Returns:
            (allowed, current_count, reset_time_seconds)
        """
        try:
            # Redis key for rate limiting
            key = f"ratelimit:{identifier}"

            # Current timestamp
            now = time.time()
            window_start = now - window

            # Remove old entries outside window
            await redis_client.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            current_count = await redis_client.zcard(key)

            if current_count < limit:
                # Add current request
                await redis_client.zadd(key, {str(now): now})

                # Set expiry on key (window + buffer)
                await redis_client.expire(key, window + 10)

                # Calculate reset time (time until oldest request expires)
                oldest_scores = await redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_scores:
                    oldest_time = oldest_scores[0][1]
                    reset_time = int(window - (now - oldest_time))
                else:
                    reset_time = window

                return True, current_count + 1, reset_time
            else:
                # Rate limit exceeded
                # Calculate when the oldest request will expire
                oldest_scores = await redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_scores:
                    oldest_time = oldest_scores[0][1]
                    reset_time = int(window - (now - oldest_time))
                else:
                    reset_time = window

                return False, current_count, reset_time

        except Exception as e:
            # If Redis fails, allow the request (fail open)
            logger.error("rate_limit_check_failed", error=str(e))
            return True, 0, 0


class SubscriptionRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting based on subscription plan limits.

    Tracks API requests per month and enforces plan limits.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """Check subscription usage limits."""
        # Skip for certain paths
        skip_paths = {"/health", "/health/db", "/health/redis", "/api/v1/payments/webhooks"}
        if request.url.path in skip_paths:
            return await call_next(request)

        # Get organization ID
        org_id = request.headers.get("X-Organization-ID")
        if not org_id:
            # No subscription check for non-org requests
            return await call_next(request)

        # TODO: Check subscription usage
        # For now, just increment counter
        try:
            key = f"usage:monthly:{org_id}"
            usage = await redis_client.incr(key)

            # Set expiry if new key (30 days)
            if usage == 1:
                await redis_client.expire(key, 30 * 24 * 60 * 60)

            # TODO: Get plan limits from database
            # For now, use high limit
            monthly_limit = 100000

            if usage > monthly_limit:
                logger.warning(
                    "monthly_limit_exceeded",
                    org_id=org_id,
                    usage=usage,
                    limit=monthly_limit,
                )

                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": {
                            "code": "MONTHLY_LIMIT_EXCEEDED",
                            "message": "Monthly API limit exceeded. Please upgrade your plan.",
                            "usage": usage,
                            "limit": monthly_limit,
                        }
                    },
                )

        except HTTPException:
            raise
        except Exception as e:
            # If Redis fails, allow the request
            logger.error("subscription_limit_check_failed", error=str(e))

        # Process request
        response = await call_next(request)

        # Add usage headers
        try:
            response.headers["X-API-Usage"] = str(usage)
            response.headers["X-API-Limit"] = str(monthly_limit)
            response.headers["X-API-Remaining"] = str(max(0, monthly_limit - usage))
        except:
            pass

        return response
