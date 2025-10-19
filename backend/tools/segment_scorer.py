
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from langchain.tools import BaseTool


def _normalise(value: float) -> float:
    return max(0.0, min(1.0, value))


class SegmentScorerTool(BaseTool):
    """Score an ICP on fit, urgency, and accessibility dimensions."""

    name = "segment_scorer"
    description = (
        "Score ICP segments. "
        "Use: segment_scorer(persona={...}, positioning={...}, weights={'fit':0.4,...})"
    )

    def _run(
        self,
        persona: Dict[str, Any],
        positioning: Optional[Dict[str, Any]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> str:  # type: ignore[override]

        weights = weights or {"fit": 0.4, "urgency": 0.35, "accessibility": 0.25}

        fit = self._score_fit(persona, positioning or {})
        urgency = self._score_urgency(persona)
        accessibility = self._score_accessibility(persona)

        overall = (
            fit * weights.get("fit", 0)
            + urgency * weights.get("urgency", 0)
            + accessibility * weights.get("accessibility", 0)
        )

        payload = {
            "fit": round(fit, 3),
            "urgency": round(urgency, 3),
            "accessibility": round(accessibility, 3),
            "overall": round(overall, 3),
        }
        return json.dumps(payload)

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        return self._run(*args, **kwargs)

    def _score_fit(self, persona: Dict[str, Any], positioning: Dict[str, Any]) -> float:
        word = (positioning or {}).get("word", "").lower()
        pains = " ".join(persona.get("psychographics", {}).get("fears", []))[:500].lower()
        gains = " ".join(persona.get("psychographics", {}).get("desires", []))[:500].lower()

        score = 0.5
        if word and word in pains:
            score += 0.25
        if word and word in gains:
            score += 0.15
        if persona.get("industry") and positioning.get("industry") == persona["industry"]:
            score += 0.1

        return _normalise(score)

    def _score_urgency(self, persona: Dict[str, Any]) -> float:
        signals = persona.get("psychographics", {}).get("fears", [])
        score = 0.3 + 0.1 * len(signals)
        if persona.get("budget", "").lower() in {"high", "enterprise"}:
            score += 0.2
        return _normalise(score)

    def _score_accessibility(self, persona: Dict[str, Any]) -> float:
        channels = persona.get("behaviors", {}).get("social_media_usage", [])
        geography = persona.get("demographics", {}).get("location", "")

        score = 0.2 + 0.15 * min(len(channels), 3)
        if "remote" in geography.lower():
            score += 0.15
        if persona.get("preferred_contact") == "email":
            score += 0.1
        return _normalise(score)
