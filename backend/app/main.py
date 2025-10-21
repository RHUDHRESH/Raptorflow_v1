"""FastAPI main application."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.redis import redis_client
from app.middleware import (
    StructuredLoggingMiddleware,
    RequestContextMiddleware,
    RateLimitMiddleware,
    SubscriptionRateLimitMiddleware,
)

# Setup structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("application_starting", version="1.0.0")

    # Test Redis connection
    try:
        await redis_client.ping()
        logger.info("redis_connected")
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await redis_client.close()


# Create FastAPI app
app = FastAPI(
    title="RaptorFlow API",
    description="Cyber Threat Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# ==========================================
# Middleware
# ==========================================


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""

    async def dispatch(self, request: Request, call_next):
        import uuid

        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), camera=(), microphone=()"
        )

        # CSP (Content Security Policy)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://checkout.razorpay.com; "
            "connect-src 'self' https://api.razorpay.com https://*.supabase.co; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline'; "
            "frame-src 'self' https://api.razorpay.com; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response


# Add middleware (order matters!)
# Note: Middleware is applied in reverse order (last added = first executed)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(StructuredLoggingMiddleware)  # Logging with request tracking
app.add_middleware(RequestContextMiddleware)  # Add context to logs
app.add_middleware(RateLimitMiddleware)  # Per-minute rate limiting
app.add_middleware(SubscriptionRateLimitMiddleware)  # Monthly usage tracking
app.add_middleware(SecurityHeadersMiddleware)  # Security headers
app.add_middleware(RequestIDMiddleware)  # Request ID generation

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.CORS_ENABLED else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Exception Handlers
# ==========================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    # Log error with structured logging
    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True if settings.DEBUG else False,
    )

    # Return error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else None,
                "trace_id": getattr(request.state, "request_id", None),
            }
        },
    )


# ==========================================
# Health Check Routes
# ==========================================


@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/health/db")
async def health_check_db():
    """Database health check."""
    from app.db.session import engine
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            start = time.time()
            await conn.execute(text("SELECT 1"))
            latency_ms = int((time.time() - start) * 1000)

        return {"status": "healthy", "latency_ms": latency_ms}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)},
        )


@app.get("/health/redis")
async def health_check_redis():
    """Redis health check."""
    try:
        start = time.time()
        await redis_client.ping()
        latency_ms = int((time.time() - start) * 1000)

        return {"status": "healthy", "latency_ms": latency_ms}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)},
        )


# ==========================================
# API Routes
# ==========================================

# Import routers
from app.api.v1.endpoints import payments, organizations, projects, users, indicators

# Include routers
app.include_router(payments.router, prefix="/api/v1", tags=["payments"])
app.include_router(organizations.router, prefix="/api/v1", tags=["organizations"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(indicators.router, prefix="/api/v1", tags=["indicators"])

# TODO: Add more routers when models are ready
# from app.api.v1.endpoints import threat_actors, campaigns, vulnerabilities
# app.include_router(threat_actors.router, prefix="/api/v1")
# app.include_router(campaigns.router, prefix="/api/v1")
# app.include_router(vulnerabilities.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "RaptorFlow API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else None,
        "health": "/health",
    }


@app.get("/api/v1")
async def api_info():
    """API v1 information."""
    return {
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "users": "/api/v1/users",
            "organizations": "/api/v1/organizations",
            "projects": "/api/v1/projects",
            "indicators": "/api/v1/indicators",
            "payments": "/api/v1/payments",
            "docs": "/docs" if settings.DEBUG else None,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
