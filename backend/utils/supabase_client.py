
"""Supabase client helper with a graceful in-memory fallback for local development."""

from __future__ import annotations

import logging
import os
import uuid
from collections import defaultdict
from types import SimpleNamespace
from typing import Any, DefaultDict, Dict, Iterable, List, Optional

try:
    from supabase import Client, create_client  # type: ignore
except Exception:  # pragma: no cover - supabase may not be installed locally
    Client = Any  # type: ignore
    create_client = None  # type: ignore

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None


class InMemoryQuery:
    """Very small subset of the Supabase query interface for tests/local dev."""

    def __init__(self, tables: DefaultDict[str, List[Dict[str, Any]]], table_name: str):
        self._tables = tables
        self._table_name = table_name
        self._filters: List[tuple[str, Any]] = []
        self._limit: Optional[int] = None
        self._order_field: Optional[str] = None
        self._order_desc = False
        self._single = False
        self._operation: Optional[str] = None
        self._payload: Any = None

    # Query modifiers -----------------------------------------------------
    def select(self, *_: Any) -> "InMemoryQuery":
        self._operation = "select"
        return self

    def insert(self, payload: Any) -> "InMemoryQuery":
        self._operation = "insert"
        self._payload = payload
        return self

    def update(self, payload: Dict[str, Any]) -> "InMemoryQuery":
        self._operation = "update"
        self._payload = payload
        return self

    def delete(self) -> "InMemoryQuery":
        self._operation = "delete"
        return self

    def eq(self, field: str, value: Any) -> "InMemoryQuery":
        self._filters.append((field, value))
        return self

    def order(self, field: str, desc: bool = False) -> "InMemoryQuery":
        self._order_field = field
        self._order_desc = desc
        return self

    def limit(self, count: int) -> "InMemoryQuery":
        self._limit = count
        return self

    def single(self) -> "InMemoryQuery":
        self._single = True
        return self

    # Execution -----------------------------------------------------------
    def execute(self) -> SimpleNamespace:
        table = self._tables[self._table_name]
        rows = self._apply_filters(table)

        if self._operation == "insert":
            payload = self._payload
            if isinstance(payload, dict):
                payload = [payload]
            inserted = []
            for item in payload:
                record = dict(item)
                record.setdefault("id", str(uuid.uuid4()))
                table.append(record)
                inserted.append(record)
            return SimpleNamespace(data=inserted)

        if self._operation == "update":
            for row in rows:
                row.update(self._payload)
            return SimpleNamespace(data=rows)

        if self._operation == "delete":
            for row in list(rows):
                table.remove(row)
            return SimpleNamespace(data=rows)

        # SELECT behaviour
        if self._order_field:
            rows.sort(key=lambda item: item.get(self._order_field), reverse=self._order_desc)
        if self._limit is not None:
            rows = rows[: self._limit]

        if self._single:
            return SimpleNamespace(data=rows[0] if rows else None)
        return SimpleNamespace(data=rows)

    # Helpers -------------------------------------------------------------
    def _apply_filters(self, table: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = []
        for row in table:
            if all(row.get(field) == value for field, value in self._filters):
                rows.append(row)
        return rows


class InMemorySupabaseClient:
    """Simplified Supabase client used when credentials are not present."""

    def __init__(self):
        self._tables: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)

    def table(self, name: str) -> InMemoryQuery:
        return InMemoryQuery(self._tables, name)


def _create_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if url and key and create_client:
        logger.debug("Initialising Supabase client for %s", url)
        return create_client(url, key)

    logger.warning("SUPABASE credentials missing; using in-memory store for tests/local runs.")
    return InMemorySupabaseClient()  # type: ignore


def get_supabase_client() -> Client:
    """Return a singleton Supabase client instance (real or in-memory)."""
    global _supabase_client  # pylint: disable=global-statement

    if _supabase_client is None:
        _supabase_client = _create_supabase_client()
    return _supabase_client
