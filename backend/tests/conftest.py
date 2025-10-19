import os
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

# Ensure the backend package is importable when tests execute from the repo root
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from main import app  # type: ignore  # pylint: disable=wrong-import-position
from utils.supabase_client import get_supabase_client  # type: ignore  # pylint: disable=wrong-import-position

# Ensure tests run in a deterministic environment
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def supabase() -> Any:
    """Provide the (possibly in-memory) Supabase client."""
    return get_supabase_client()


@pytest.fixture
def mock_gemini(mocker: pytest.MockFixture):
    """Mock Gemini responses for deterministic tests."""
    mock = mocker.patch("backend.utils.gemini_client.get_gemini_client")
    instance = mock.return_value
    instance.generate_content.return_value.text = '{"result": "ok"}'
    return instance


@pytest.fixture
def mock_perplexity(mocker: pytest.MockFixture):
    """Mock Perplexity API calls used by research tooling."""
    mock = mocker.patch("backend.tools.perplexity_search.PerplexitySearchTool._run")
    mock.return_value = '{"findings": "Test findings", "citations": []}'
    return mock


@pytest.fixture
def sample_business() -> dict[str, Any]:
    """Example business payload used across multiple tests."""
    return {
        "name": "Test Corp",
        "industry": "SaaS",
        "location": "Chennai, India",
        "description": "Test business description",
        "goals": "Generate 100 leads per month",
    }


@pytest.fixture
def sample_positioning() -> dict[str, Any]:
    """Example positioning data."""
    return {
        "word": "innovation",
        "rationale": "Test rationale",
        "big_idea": "Test big idea",
        "purple_cow": "Test purple cow",
        "differentiation_score": 0.85,
    }


@pytest.fixture
def sample_icp() -> dict[str, Any]:
    """Example ICP definition for downstream scoring."""
    return {
        "name": "Sarah",
        "age": 34,
        "archetype": "The Busy Professional",
        "demographics": {
            "age": 34,
            "income": "$85,000",
            "location": "Mumbai, India",
        },
        "psychographics": {
            "core_values": ["efficiency", "growth"],
            "fears": ["wasting time", "falling behind"],
            "desires": ["career advancement", "work-life balance"],
        },
    }
