#!/usr/bin/env python3
"""
Utility to verify that critical dependencies can be imported.

The module can be executed directly for a quick sanity check or
consumed by pytest, where each dependency is tested individually.
"""

from __future__ import annotations

import importlib
import sys
from typing import Iterable

import pytest


# Keep the list central so both pytest and the CLI entry point use the same data.
CRITICAL_DEPS = (
    "fastapi",
    "uvicorn",
    "pydantic",
    "dotenv",
    "supabase",
    "redis",
    "sqlalchemy",
    "razorpay",
    "langchain",
    "openai",
    "tiktoken",
    "aiohttp",
    "tenacity",
    "yaml",  # PyYAML
    "requests",
    "numpy",
    "pandas",
    "httpx",
    "aiofiles",
    "multipart",  # python-multipart
    "bleach",
    "slowapi",
    "prometheus_client",
    "cryptography",
    "jose",  # python-jose
    "passlib",
    "google.auth",
    "jwt",  # pyjwt
    "sklearn",  # scikit-learn
    "chromadb",
    "jinja2",
    "mangum",
    "pytest",
    "structlog",
    "bandit",
    "safety",
)

OPTIONAL_DEPS = {
    # `supabase` pulls in websockets extras that are not available in minimal
    # environments; in that case our runtime falls back to the in-memory client.
    "supabase": "Supabase client optional during local testing (websockets extra missing)",
}


def _import_ok(module_name: str) -> bool:
    """Attempt to import a module, returning True on success."""
    try:
        importlib.import_module(module_name)
        print(f"[OK] {module_name}")
        return True
    except ImportError as exc:
        print(f"[FAIL] {module_name}: {exc}")
        return False
    except Exception as exc:  # defensive: catch unexpected runtime errors
        print(f"[ERROR] {module_name}: {exc}")
        return False


@pytest.mark.parametrize("module_name", CRITICAL_DEPS)
def test_importable(module_name: str) -> None:
    """Pytest entry point for dependency import validation."""
    if not _import_ok(module_name):
        reason = OPTIONAL_DEPS.get(module_name)
        if reason:
            pytest.skip(reason)
        pytest.fail(f"{module_name} failed to import")


def _run_cli(modules: Iterable[str]) -> int:
    """Execute the import checks synchronously for CLI usage."""
    print("Testing critical dependencies...")
    failed = []
    for module in modules:
        if not _import_ok(module) and module not in OPTIONAL_DEPS:
            failed.append(module)
    print(f"\nResults: {len(modules) - len(failed)}/{len(modules)} imports successful")

    if failed:
        print(f"Failed imports: {', '.join(failed)}")
    else:
        print("All critical dependencies can be imported successfully!")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(_run_cli(CRITICAL_DEPS))
