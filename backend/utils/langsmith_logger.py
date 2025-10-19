"""Utility helpers for routing LangGraph traces into LangSmith when available."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, Iterable, Optional

try:
    from langsmith import Client  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Client = None  # type: ignore

logger = logging.getLogger(__name__)


def _build_client() -> Optional["Client"]:
    """Initialise a LangSmith client when the SDK and API key are available."""
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key or Client is None:
        return None
    try:
        return Client(api_key=api_key, project=os.getenv("LANGSMITH_PROJECT", "raptorflow-adapt"))
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to initialise LangSmith client: %s", exc)
        return None


_client = _build_client()


def log_event(event: str, payload: Dict[str, Any]) -> None:
    """
    Send a lightweight event to LangSmith while mirroring the entry to the local log.

    Parameters
    ----------
    event:
        Descriptive event name (e.g. ``research.completed``).
    payload:
        JSON-serialisable metadata associated with the event.
    """
    logger.info("LangSmith event %s: %s", event, payload)

    if _client is None:
        return

    try:  # pragma: no cover - network call
        _client.create_event(event=event, metadata=payload)
    except Exception as exc:
        logger.debug("LangSmith event dispatch failed (%s)", exc)


@contextmanager
def trace(name: str, metadata: Optional[Dict[str, Any]] = None) -> Iterable[None]:
    """
    Context manager that records start/finish milestones for a logical operation.

    Example
    -------
    .. code-block:: python

        with trace("research.agent", {"business_id": biz_id}):
            result = await research_agent.ainvoke(state)
    """
    log_event(f"{name}.start", metadata or {})
    try:
        yield
    finally:
        log_event(f"{name}.end", metadata or {})
