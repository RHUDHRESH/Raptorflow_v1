"""Logging middleware for FastAPI."""

import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import LogContext, get_logger

logger = get_logger(__name__)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with structured logging.

    Adds:
    - Request ID
    - Request method, path, query params
    - Response status code
    - Request duration
    - User information (if authenticated)
    - Organization context (if present)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate request ID
        request_id = str(uuid4())
        request.state.request_id = request_id

        # Start timer
        start_time = time.time()

        # Extract request details
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_host = request.client.host if request.client else None

        # Get user and org context if available
        user_id = getattr(request.state, "user_id", None)
        org_id = request.headers.get("X-Organization-ID")

        # Log request start
        with LogContext(
            request_id=request_id,
            method=method,
            path=path,
            client_host=client_host,
            user_id=user_id,
            org_id=org_id,
        ):
            logger.info(
                "request_started",
                query_params=query_params if query_params else None,
            )

            try:
                # Process request
                response = await call_next(request)

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Add headers
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Response-Time"] = f"{duration_ms}ms"

                # Log successful response
                logger.info(
                    "request_completed",
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )

                return response

            except Exception as e:
                # Calculate duration for failed request
                duration_ms = int((time.time() - start_time) * 1000)

                # Log error
                logger.error(
                    "request_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_ms=duration_ms,
                    exc_info=True,
                )

                # Re-raise exception to be handled by error handlers
                raise


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request context to all logs within the request lifecycle.

    This uses structlog's context variables to automatically include
    request_id, user_id, and org_id in all log statements.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request context to logs."""
        # Get request ID (should be set by previous middleware)
        request_id = getattr(request.state, "request_id", str(uuid4()))

        # Get user context if authenticated
        user_id = getattr(request.state, "user_id", None)
        org_id = request.headers.get("X-Organization-ID")

        # Bind context for all logs in this request
        with LogContext(
            request_id=request_id,
            user_id=user_id,
            org_id=org_id,
        ):
            response = await call_next(request)
            return response
