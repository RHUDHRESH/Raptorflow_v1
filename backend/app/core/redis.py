"""Redis client for caching and rate limiting."""

import redis.asyncio as redis
from app.core.config import settings

# Create Redis client
redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
)


async def get_redis():
    """Get Redis client (for dependency injection)."""
    return redis_client
