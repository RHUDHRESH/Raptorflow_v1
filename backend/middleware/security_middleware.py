"""
Security Middleware for RaptorFlow ADAPT
Implements comprehensive security controls for production deployment
"""

import os
import time
import re
import json
import hashlib
import hmac
from typing import Dict, List, Optional, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import bleach
import logging
from datetime import datetime, timedelta
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

class SecurityException(Exception):
    """Custom security exception"""
    pass

class CostLimitExceeded(Exception):
    """Custom cost limit exception"""
    pass

class AISafetyMiddleware:
    """Advanced AI safety and input validation"""
    
    def __init__(self):
        self.malicious_patterns = [
            r'ignore.*previous.*instruction',
            r'system.*prompt',
            r'expose.*data',
            r'admin.*access',
            r'bypass.*security',
            r'database.*password',
            r'secret.*key',
            r'internal.*api',
            r'\$\{.*\}',  # JNDI injection
            r'<script.*?>.*?</script>',  # XSS
            r'javascript:',
            r'onload=',
            r'onerror=',
        ]
        
        self.max_input_length = 50000
        self.max_requests_per_minute = {
            'intake': 5,
            'research': 2,
            'positioning': 3,
            'icps': 3,
            'moves': 10,
            'analytics': 20
        }
    
    async def validate_input(self, text: str, field_name: str = "input") -> bool:
        """Validate and sanitize user input"""
        if not text:
            return True
        
        # Check length limits
        if len(text) > self.max_input_length:
            raise SecurityException(f"{field_name} exceeds maximum length")
        
        # Check for malicious patterns
        for pattern in self.malicious_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                logger.warning(f"Malicious pattern detected in {field_name}: {pattern}")
                raise SecurityException(f"Potentially malicious content detected in {field_name}")
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"('|(\\')|(;)|(\\;))(\s)*(union|select|insert|update|delete|drop|create|alter|exec|execute)",
            r"(\s)*(or|and)(\s)+(\w)+(\s)*(=|like|>|<)",
            r"(--)(.*)",
            r"(/\*)(.*?)(\*/)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected in {field_name}")
                raise SecurityException(f"Invalid content detected in {field_name}")
        
        return True
    
    async def sanitize_output(self, output: str) -> str:
        """Sanitize AI output to prevent data leakage"""
        if not output:
            return output
        
        try:
            # Remove email addresses
            output = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED]', output, flags=re.IGNORECASE)
            
            # Remove phone numbers (more comprehensive pattern)
            output = re.sub(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b', '[REDACTED]', output)
            
            # Remove credit card numbers (Luhn algorithm check would be better)
            output = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[REDACTED]', output)
            
            # Remove API keys (more specific patterns)
            output = re.sub(r'\b[A-Za-z0-9_-]{20,}\b', '[REDACTED]', output)
            output = re.sub(r'(sk_|pk_|tok_|secret_|api_key_)[A-Za-z0-9_-]+', '[REDACTED]', output, flags=re.IGNORECASE)
            
            # Remove internal system information
            output = re.sub(r'(internal|system|admin|backend|private).*?(api|endpoint|url|key|secret)', r'\1 \2 [REDACTED]', output, flags=re.IGNORECASE)
            
            # Remove URLs that might be internal
            output = re.sub(r'https?://(?:localhost|127\.0\.0\.1|internal|private)[^\s]*', '[REDACTED]', output, flags=re.IGNORECASE)
            
        except Exception as e:
            logger.error(f"Error in output sanitization: {e}")
            # Return original output if sanitization fails
        
        return output

class CostControlMiddleware:
    """Advanced cost control for AI operations"""
    
    def __init__(self):
        self.daily_limits = {
            'basic': 10.0,      # $10/day
            'pro': 50.0,        # $50/day
            'enterprise': 200.0 # $200/day
        }
        
        # Redis for cost tracking (fallback to in-memory if not available)
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True
            )
            self.redis_client.ping()
        except Exception:
            logger.warning("Redis not available, using in-memory cost tracking")
            self.redis_client = None
            self.memory_store = {}
    
    async def get_user_tier(self, user_id: str) -> str:
        """Get user's subscription tier"""
        # This would typically query your database
        # For now, return basic as default
        return 'basic'
    
    async def get_daily_spend(self, user_id: str) -> float:
        """Get user's current daily spend"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"cost:{user_id}:{today}"
        
        if self.redis_client:
            try:
                spend = self.redis_client.get(key)
                return float(spend) if spend else 0.0
            except Exception:
                pass
        
        # Fallback to memory store
        if hasattr(self, 'memory_store'):
            return self.memory_store.get(key, 0.0)
        
        return 0.0
    
    async def track_cost(self, user_id: str, actual_cost: float):
        """Track actual cost and update database"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"cost:{user_id}:{today}"
        
        if self.redis_client:
            try:
                self.redis_client.incrbyfloat(key, actual_cost)
                self.redis_client.expire(key, 86400)  # 24 hours
            except Exception:
                pass
        
        # Fallback to memory store
        if hasattr(self, 'memory_store'):
            self.memory_store[key] = self.memory_store.get(key, 0.0) + actual_cost
        
        # Alert if approaching limit
        current_spend = await self.get_daily_spend(user_id)
        user_tier = await self.get_user_tier(user_id)
        limit = self.daily_limits[user_tier]
        
        if current_spend > limit * 0.8:
            await self.send_alert(user_id, f"Approaching daily cost limit: ${current_spend:.2f}/${limit:.2f}")
    
    async def check_limit(self, user_id: str, estimated_cost: float) -> bool:
        """Check if operation would exceed cost limit"""
        current_spend = await self.get_daily_spend(user_id)
        user_tier = await self.get_user_tier(user_id)
        limit = self.daily_limits[user_tier]
        
        if current_spend + estimated_cost > limit:
            raise CostLimitExceeded(f"Daily limit of ${limit} would be exceeded")
        
        return True
    
    async def send_alert(self, user_id: str, message: str):
        """Send cost alert (implement your notification system)"""
        logger.warning(f"Cost alert for user {user_id}: {message}")
        # TODO: Implement email/Slack notifications

class RateLimitMiddleware:
    """Advanced rate limiting with Redis backend"""
    
    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address)
        self.limits = {
            'intake': '5/minute',
            'research': '2/minute',
            'positioning': '3/minute',
            'icps': '3/minute',
            'moves': '10/minute',
            'analytics': '20/minute',
            'default': '100/minute'
        }
    
    def get_limit_for_endpoint(self, path: str) -> str:
        """Get rate limit for specific endpoint"""
        for endpoint, limit in self.limits.items():
            if endpoint in path:
                return limit
        return self.limits['default']

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS for HTTPS
        if os.getenv('ENVIRONMENT') == 'production':
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize all incoming requests"""
    
    def __init__(self, app):
        super().__init__(app)
        self.ai_safety = AISafetyMiddleware()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip validation for health checks and metrics
        if request.url.path in ['/health', '/metrics', '/']:
            return await call_next(request)
        
        # Validate JSON payload
        if request.method in ['POST', 'PUT', 'PATCH'] and 'application/json' in request.headers.get('content-type', ''):
            try:
                body = await request.body()
                if body:
                    data = json.loads(body.decode('utf-8'))
                    await self.validate_payload(data, request.url.path)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON payload"
                )
            except SecurityException as e:
                logger.warning(f"Security validation failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
        
        return await call_next(request)
    
    async def validate_payload(self, data: dict, path: str):
        """Validate payload based on endpoint"""
        if not isinstance(data, dict):
            return
            
        # Common fields validation
        for field_name, value in data.items():
            try:
                if isinstance(value, str):
                    await self.ai_safety.validate_input(value, field_name)
                elif isinstance(value, dict):
                    await self.validate_payload(value, path)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, (str, dict)):
                            if isinstance(item, str):
                                await self.ai_safety.validate_input(item, field_name)
                            else:
                                await self.validate_payload(item, path)
            except SecurityException:
                # Re-raise security exceptions
                raise
            except Exception as e:
                logger.error(f"Error validating field {field_name}: {e}")
                # Continue validation for other fields

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """JWT-based authentication middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.jwt_secret = os.getenv('JWT_SECRET')
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required")
        
        self.public_paths = [
            '/',
            '/health',
            '/metrics',
            '/docs',
            '/openapi.json',
            '/api/intake',  # Allow business creation
            '/api/razorpay/webhook',  # Webhooks
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Extract and validate JWT token
        authorization = request.headers.get('Authorization')
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization.split(' ')[1]
        try:
            import jwt
            import time
            
            # Decode JWT token
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            # Check if token is expired
            if payload.get('exp', 0) < time.time():
                raise ValueError("Token expired")
            
            # Add user info to request state
            request.state.user_id = payload.get('user_id', 'unknown')
            request.state.user_tier = payload.get('tier', 'basic')
            
        except ImportError:
            # Fallback if PyJWT is not installed
            logger.warning("PyJWT not installed, using basic token validation")
            if not token or len(token) < 10:
                raise ValueError("Invalid token")
            request.state.user_id = "temp_user_id"
        except Exception as e:
            logger.warning(f"Authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return await call_next(request)

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Comprehensive audit logging"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger('audit')
        
        # Configure audit logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        self.logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"IP: {request.client.host if request.client else 'unknown'} - "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )
        
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        self.logger.info(
            f"Response: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"Path: {request.url.path}"
        )
        
        # Log security events
        if response.status_code >= 400:
            self.logger.warning(
                f"Security Event: {response.status_code} - "
                f"Path: {request.url.path} - "
                f"IP: {request.client.host if request.client else 'unknown'}"
            )
        
        return response

# Initialize middleware instances
ai_safety = AISafetyMiddleware()
cost_control = CostControlMiddleware()
rate_limiter = RateLimitMiddleware()

def get_ai_safety():
    """Get AI safety instance"""
    return ai_safety

def get_cost_control():
    """Get cost control instance"""
    return cost_control

def get_rate_limiter():
    """Get rate limiter instance"""
    return rate_limiter
