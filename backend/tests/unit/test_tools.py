
from __future__ import annotations

import json
from typing import Any

import pytest

from tools.competitor_ladder import CompetitorLadderTool
from tools.differentiation import DifferentiationAnalyzerTool
from tools.positioning_kb import PositioningKnowledgeBaseTool


class TestCompetitorLadderTool:
    def test_build_ladder(self, mock_perplexity: Any, sample_business: dict[str, Any], mock_gemini: Any):
        """Building a ladder should return structured competitor data."""
        tool = CompetitorLadderTool()
        result = json.loads(
            tool._run(  # pylint: disable=protected-access
                action="build",
                business_id="test-id",
                industry=sample_business["industry"],
            )
        )

        assert result["success"] is True
        assert "competitors" in result

    def test_analyze_gap(self, mock_perplexity: Any, mock_gemini: Any):
        """Gap analysis should surface opportunity slots."""
        tool = CompetitorLadderTool()
        tool.supabase.table("competitor_ladder").insert(
            {
                "business_id": "test-id",
                "competitor_name": "Comp A",
                "word_owned": "speed",
                "position_strength": 0.9,
                "evidence": {},
            }
        ).execute()

        result = json.loads(
            tool._run(  # pylint: disable=protected-access
                action="analyze_gap",
                business_id="test-id",
                industry="SaaS",
            )
        )
        assert "gap_opportunities" in result


class TestPositioningKnowledgeBase:
    def test_get_principle(self):
        """Principles should be retrievable by canonical key."""
        tool = PositioningKnowledgeBaseTool()
        result = json.loads(tool._run(action="get_principle", principle="law_of_focus"))  # pylint: disable=protected-access

        assert "principle" in result
        assert "summary" in result

    def test_search_similar(self):
        """Semantic search returns up to the requested number of snippets."""
        tool = PositioningKnowledgeBaseTool()
        result = json.loads(
            tool._run(  # pylint: disable=protected-access
                action="search_similar",
                query="differentiation strategy",
                top_k=3,
            )
        )
        assert len(result["results"]) <= 3


class TestDifferentiationAnalyzer:
    def test_analyze_differentiation(self, sample_positioning: dict[str, Any]):
        """Differentiation scoring should fall within [0, 1]."""
        tool = DifferentiationAnalyzerTool()
        competitors = [
            {"competitor_name": "Comp A", "word_owned": "innovation", "position_strength": 0.8}
        ]

        result = json.loads(
            tool._run(  # pylint: disable=protected-access
                action="analyze",
                positioning=sample_positioning["word"],
                competitor_ladder=competitors,
            )
        )

        assert 0 <= result["differentiation_score"] <= 1
        assert "conflicts" in result
