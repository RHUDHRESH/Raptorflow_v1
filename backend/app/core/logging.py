"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def add_app_context(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to log events."""
    event_dict["app"] = "raptorflow"
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def censor_sensitive_data(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Censor sensitive data from logs."""
    sensitive_keys = {
        "password",
        "token",
        "secret",
        "api_key",
        "authorization",
        "cookie",
        "session",
    }

    def _censor_dict(d: dict[str, Any]) -> dict[str, Any]:
        """Recursively censor sensitive keys in dictionaries."""
        censored = {}
        for key, value in d.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                censored[key] = "***REDACTED***"
            elif isinstance(value, dict):
                censored[key] = _censor_dict(value)
            elif isinstance(value, list):
                censored[key] = [
                    _censor_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                censored[key] = value
        return censored

    return _censor_dict(event_dict)


def setup_logging() -> None:
    """
    Configure structured logging.

    Sets up structlog with:
    - JSON output in production
    - Pretty console output in development
    - Request ID tracking
    - Sensitive data censoring
    - Timestamp in ISO format
    """
    # Determine output format based on environment
    is_development = settings.DEBUG

    # Shared processors for all environments
    shared_processors: list[Processor] = [
        # Add log level to event dict
        structlog.stdlib.add_log_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add application context
        add_app_context,
        # Censor sensitive data
        censor_sensitive_data,
        # Add stack info if exception
        structlog.processors.StackInfoRenderer(),
        # Format exceptions
        structlog.processors.format_exc_info,
    ]

    if is_development:
        # Development: Pretty console output with colors
        processors = shared_processors + [
            # Pretty print for console
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ]
    else:
        # Production: JSON output
        processors = shared_processors + [
            # JSON output for log aggregation
            structlog.processors.JSONRenderer(),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger

    Example:
        ```python
        from app.core.logging import get_logger

        logger = get_logger(__name__)

        logger.info("user_created", user_id=user.id, email=user.email)
        logger.error("payment_failed", payment_id=payment.id, error=str(e))
        ```
    """
    return structlog.get_logger(name)


# Context manager for request-scoped logging
class LogContext:
    """
    Context manager for adding request-scoped context to logs.

    Example:
        ```python
        with LogContext(request_id="abc-123", user_id="user-456"):
            logger.info("processing_request")
            # All logs within this context will include request_id and user_id
        ```
    """

    def __init__(self, **context: Any):
        """
        Initialize log context.

        Args:
            **context: Key-value pairs to add to all logs in this context
        """
        self.context = context
        self.token: structlog.contextvars.Token | None = None

    def __enter__(self) -> "LogContext":
        """Enter context and bind context variables."""
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and unbind context variables."""
        if self.token is not None:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


# Pre-configured logger for imports
logger = get_logger(__name__)
