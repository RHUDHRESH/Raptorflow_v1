from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from datetime import datetime, timedelta

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Redis for distributed rate limiting
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=6379,
    decode_responses=True
)

class TieredRateLimiter:
    """Rate limiting based on subscription tier"""
    
    LIMITS = {
        'basic': {
            'api_calls_per_hour': 100,
            'research_per_day': 5,
            'positioning_per_day': 3,
            'moves_per_day': 5,
            'ai_tokens_per_day': 50_000
        },
        'pro': {
            'api_calls_per_hour': 500,
            'research_per_day': 20,
            'positioning_per_day': 10,
            'moves_per_day': 20,
            'ai_tokens_per_day': 200_000
        },
        'enterprise': {
            'api_calls_per_hour': 2000,
            'research_per_day': 100,
            'positioning_per_day': 50,
            'moves_per_day': 100,
            'ai_tokens_per_day': 1_000_000
        }
    }
    
    @staticmethod
    async def check_limit(
        business_id: str,
        tier: str,
        resource: str
    ) -> bool:
        """Check if user has exceeded their tier limit"""
        
        limits = TieredRateLimiter.LIMITS.get(tier, TieredRateLimiter.LIMITS['basic'])
        limit_key = f"{business_id}:{resource}:{datetime.now().strftime('%Y-%m-%d')}"
        
        current = redis_client.get(limit_key)
        current_count = int(current) if current else 0
        
        max_limit = limits.get(resource, 0)
        
        if current_count >= max_limit:
            raise HTTPException(
                status_code=429,
                detail={
                    'error': 'Rate limit exceeded',
                    'resource': resource,
                    'limit': max_limit,
                    'current': current_count,
                    'tier': tier,
                    'upgrade_to': 'pro' if tier == 'basic' else 'enterprise'
                }
            )
        
        # Increment counter
        redis_client.incr(limit_key)
