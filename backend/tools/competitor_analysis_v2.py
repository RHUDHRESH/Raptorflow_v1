"""
COMPETITOR ANALYSIS TOOLS v2 - Advanced competitive intelligence
Builds positioning ladders, analyzes differentiation, maps competitive conflicts
"""
import logging
import json
from typing import Dict, Any, List, Optional
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class CompetitorLadderBuilderTool(BaseTool):
    """Build competitive positioning ladder"""

    def __init__(self):
        super().__init__(
            name="competitor_ladder_builder",
            description="Build and analyze competitor positioning ladder"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        if "competitors" not in kwargs or not isinstance(kwargs["competitors"], list):
            raise ValueError("competitors must be a non-empty list")

    async def _execute(self, competitors: List[Dict], industry: str = "", **kwargs) -> Dict[str, Any]:
        """Build competitor ladder with positioning analysis"""
        logger.info(f"Building ladder for {len(competitors)} competitors")

        try:
            ladder = []
            max_strength = 0.0

            # Analyze each competitor
            for comp in competitors:
                if not comp.get("name"):
                    continue

                # Score positioning strength (0.0-1.0)
                strength = self._calculate_positioning_strength(comp)
                max_strength = max(max_strength, strength)

                ladder.append({
                    "position": len(ladder) + 1,
                    "competitor": comp.get("name"),
                    "word_owned": comp.get("positioning_word", "Unknown"),
                    "positioning": comp.get("positioning", ""),
                    "positioning_strength": round(strength, 2),
                    "target_market": comp.get("target_market", ""),
                    "pricing": comp.get("pricing", ""),
                    "unique_advantages": comp.get("advantages", []),
                    "weaknesses": comp.get("weaknesses", []),
                    "market_share_estimate": comp.get("market_share", ""),
                    "trajectory": comp.get("trajectory", "stable")  # growing, stable, declining
                })

            # Sort by positioning strength
            ladder.sort(key=lambda x: x["positioning_strength"], reverse=True)

            # Identify positioning gaps (opportunities)
            gaps = self._identify_gaps(ladder)

            # Calculate market coverage
            total_strength = sum(c["positioning_strength"] for c in ladder)
            coverage = round(total_strength / (max_strength * len(ladder)) if ladder else 0, 2)

            return {
                "success": True,
                "ladder": ladder,
                "positioning_gaps": gaps,
                "market_coverage": coverage,
                "industry": industry,
                "analysis_count": len(ladder),
                "recommendation": self._get_recommendation(gaps, ladder)
            }

        except Exception as e:
            logger.error(f"Ladder building failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _calculate_positioning_strength(self, competitor: Dict) -> float:
        """Calculate positioning strength 0.0-1.0"""
        strength = 0.0

        # Brand recognition (0-0.3)
        if competitor.get("brand_recognition") == "very_high":
            strength += 0.3
        elif competitor.get("brand_recognition") == "high":
            strength += 0.2
        elif competitor.get("brand_recognition") == "medium":
            strength += 0.1

        # Market position (0-0.3)
        if competitor.get("market_position") == "leader":
            strength += 0.3
        elif competitor.get("market_position") == "strong":
            strength += 0.2
        elif competitor.get("market_position") == "established":
            strength += 0.1

        # Positioning clarity (0-0.2)
        if competitor.get("positioning_clarity") == "very_clear":
            strength += 0.2
        elif competitor.get("positioning_clarity") == "clear":
            strength += 0.1

        # Customer loyalty (0-0.2)
        if competitor.get("customer_loyalty") == "very_high":
            strength += 0.2
        elif competitor.get("customer_loyalty") == "high":
            strength += 0.1

        return min(1.0, strength)

    def _identify_gaps(self, ladder: List[Dict]) -> List[Dict]:
        """Identify positioning gaps and opportunities"""
        gaps = []

        if len(ladder) < 2:
            return gaps

        # Check for underserved positioning words
        used_words = set(c["word_owned"] for c in ladder if c["word_owned"] != "Unknown")

        common_positions = [
            "Speed", "Quality", "Price", "Reliability", "Innovation",
            "Sustainability", "Luxury", "Accessibility", "Safety", "Community",
            "Personalization", "Simplicity", "Power", "Efficiency", "Trust"
        ]

        for word in common_positions:
            if word not in used_words:
                gaps.append({
                    "positioning_word": word,
                    "opportunity_level": "high",
                    "reasoning": f"{word} positioning is unowned in this market"
                })

        # Identify strength gaps
        strengths = [c["positioning_strength"] for c in ladder]
        if strengths:
            avg_strength = sum(strengths) / len(strengths)
            if max(strengths) - min(strengths) > 0.5:
                gaps.append({
                    "positioning_word": "Emerging Challenge",
                    "opportunity_level": "medium",
                    "reasoning": "Large strength gap between market leaders and challengers"
                })

        return gaps[:5]  # Return top 5 gaps

    def _get_recommendation(self, gaps: List[Dict], ladder: List[Dict]) -> str:
        """Get strategic recommendation based on analysis"""
        if not gaps:
            return "Market is well-covered. Consider disruptive positioning."

        top_gap = gaps[0]
        return f"Market opportunity: Own '{top_gap['positioning_word']}' positioning. Competitors are focused on other attributes."


class DifferentiationAnalyzerTool(BaseTool):
    """Analyze differentiation vs competitors"""

    def __init__(self):
        super().__init__(
            name="differentiation_analyzer",
            description="Analyze product/service differentiation against competitors"
        )

    def _validate_inputs(self, **kwargs):
        """Validate inputs"""
        if "business_positioning" not in kwargs:
            raise ValueError("business_positioning required")
        if "competitor_ladder" not in kwargs or not isinstance(kwargs["competitor_ladder"], list):
            raise ValueError("competitor_ladder must be a list")

    async def _execute(
        self,
        business_positioning: Dict,
        competitor_ladder: List[Dict],
        business_features: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze differentiation opportunities and conflicts"""
        logger.info("Analyzing differentiation against competitors")

        try:
            business_features = business_features or []
            conflicts = []
            differentiators = []

            # Extract competitor positioning words
            competitor_words = [c.get("word_owned", "") for c in competitor_ladder if c.get("word_owned")]
            business_word = business_positioning.get("word", "")

            # Check for direct conflicts
            if business_word in competitor_words:
                conflicts.append({
                    "type": "direct_conflict",
                    "word": business_word,
                    "severity": "high",
                    "description": f"'{business_word}' is already owned by competitor",
                    "mitigation": "Find unique angle or different positioning word"
                })

            # Find related conflicts
            related_words = self._find_related_words(business_word)
            for rel_word in related_words:
                if rel_word in competitor_words:
                    conflicts.append({
                        "type": "adjacent_conflict",
                        "word": rel_word,
                        "severity": "medium",
                        "description": f"'{rel_word}' is related to '{business_word}' and already owned"
                    })

            # Identify unique differentiators
            for feature in business_features:
                is_unique = True
                for comp in competitor_ladder:
                    if feature.lower() in str(comp.get("unique_advantages", [])).lower():
                        is_unique = False
                        break

                if is_unique:
                    differentiators.append({
                        "feature": feature,
                        "uniqueness_score": 0.9,
                        "type": "feature_advantage"
                    })

            # Calculate differentiation score
            total_competitors = len(competitor_ladder)
            conflicted_competitors = len([c for c in conflicts if c["type"] == "direct_conflict"])
            differentiation_score = round(1.0 - (conflicted_competitors / max(total_competitors, 1)), 2)

            return {
                "success": True,
                "business_positioning": business_word,
                "differentiation_score": differentiation_score,
                "conflicts": conflicts,
                "differentiators": differentiators,
                "recommendation": self._get_diff_recommendation(differentiation_score, conflicts),
                "defensibility_score": round(differentiation_score * 0.8 + 0.2, 2)  # Add 20% base defensibility
            }

        except Exception as e:
            logger.error(f"Differentiation analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _find_related_words(self, word: str) -> List[str]:
        """Find related positioning words"""
        word_relationships = {
            "Speed": ["Fast", "Quick", "Rapid"],
            "Quality": ["Premium", "Excellence", "Best"],
            "Price": ["Affordable", "Budget", "Value"],
            "Innovation": ["Modern", "New", "Advanced"],
            "Reliability": ["Dependable", "Trustworthy", "Stable"]
        }
        return word_relationships.get(word, [])

    def _get_diff_recommendation(self, score: float, conflicts: List[Dict]) -> str:
        """Get differentiation recommendation"""
        if score >= 0.8:
            return "Strong differentiation. Positioning is defensible."
        elif score >= 0.5:
            return "Moderate differentiation. Consider additional unique angles."
        else:
            if conflicts:
                return f"Weak differentiation. Found {len(conflicts)} positioning conflicts. Recommend repositioning."
            return "Positioning may face challenges. Strengthen unique value proposition."


class CompetitorMonitoringTool(BaseTool):
    """Monitor competitor activities and changes"""

    def __init__(self):
        super().__init__(
            name="competitor_monitoring",
            description="Monitor competitor positioning, pricing, and strategy changes"
        )

    async def _execute(
        self,
        competitors: List[Dict],
        tracking_period_days: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """Monitor competitor changes"""
        logger.info(f"Monitoring {len(competitors)} competitors")

        try:
            changes = []
            alerts = []

            for competitor in competitors:
                current = competitor.get("current_state", {})
                previous = competitor.get("previous_state", {})

                # Check for positioning changes
                if current.get("positioning") != previous.get("positioning"):
                    changes.append({
                        "competitor": competitor.get("name"),
                        "change_type": "positioning",
                        "from": previous.get("positioning"),
                        "to": current.get("positioning"),
                        "severity": "high"
                    })
                    alerts.append(f"{competitor.get('name')} changed positioning")

                # Check for pricing changes
                if current.get("pricing") != previous.get("pricing"):
                    changes.append({
                        "competitor": competitor.get("name"),
                        "change_type": "pricing",
                        "from": previous.get("pricing"),
                        "to": current.get("pricing"),
                        "severity": "medium"
                    })
                    alerts.append(f"{competitor.get('name')} adjusted pricing")

                # Check for new features
                current_features = set(current.get("features", []))
                previous_features = set(previous.get("features", []))
                new_features = current_features - previous_features

                if new_features:
                    changes.append({
                        "competitor": competitor.get("name"),
                        "change_type": "new_features",
                        "features": list(new_features),
                        "severity": "medium"
                    })

            return {
                "success": True,
                "monitoring_period_days": tracking_period_days,
                "competitors_monitored": len(competitors),
                "changes_detected": len(changes),
                "changes": changes,
                "alerts": alerts,
                "recommendation": "Review competitive changes and adjust strategy if needed"
            }

        except Exception as e:
            logger.error(f"Competitor monitoring failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class PositioningConflictDetectorTool(BaseTool):
    """Detect positioning conflicts and overlaps"""

    def __init__(self):
        super().__init__(
            name="positioning_conflict_detector",
            description="Detect overlaps and conflicts in positioning strategies"
        )

    async def _execute(
        self,
        positioning_options: List[Dict],
        competitor_ladder: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Detect conflicts between positioning options and competitors"""
        logger.info(f"Detecting conflicts for {len(positioning_options)} options")

        try:
            conflicts_per_option = []

            for i, option in enumerate(positioning_options):
                option_conflicts = []
                word = option.get("word", "")

                # Check against each competitor
                for competitor in competitor_ladder:
                    comp_word = competitor.get("word_owned", "")

                    if self._words_conflict(word, comp_word):
                        option_conflicts.append({
                            "competitor": competitor.get("competitor"),
                            "their_word": comp_word,
                            "conflict_type": "direct" if word == comp_word else "semantic",
                            "severity": 0.9 if word == comp_word else 0.5
                        })

                conflicts_per_option.append({
                    "option_number": i + 1,
                    "positioning_word": word,
                    "conflicts": option_conflicts,
                    "conflict_count": len(option_conflicts),
                    "recommendation": self._get_conflict_recommendation(option_conflicts)
                })

            # Rank options by lowest conflict
            conflicts_per_option.sort(key=lambda x: x["conflict_count"])

            return {
                "success": True,
                "positioning_options": len(positioning_options),
                "conflicts_by_option": conflicts_per_option,
                "best_option": conflicts_per_option[0] if conflicts_per_option else None,
                "summary": f"Option {conflicts_per_option[0]['option_number']} has fewest conflicts ({conflicts_per_option[0]['conflict_count']})"
            }

        except Exception as e:
            logger.error(f"Conflict detection failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _words_conflict(self, word1: str, word2: str) -> bool:
        """Check if two positioning words conflict"""
        if word1.lower() == word2.lower():
            return True

        # Check semantic similarity
        similar_sets = [
            {"fast", "speed", "quick", "rapid"},
            {"quality", "premium", "excellence"},
            {"cheap", "affordable", "budget", "value"},
            {"safe", "security", "trust", "reliable"}
        ]

        for similar_set in similar_sets:
            if word1.lower() in similar_set and word2.lower() in similar_set:
                return True

        return False

    def _get_conflict_recommendation(self, conflicts: List[Dict]) -> str:
        """Get recommendation based on conflicts"""
        if not conflicts:
            return "No conflicts detected. Positioning is unique."
        if len(conflicts) == 1:
            return "Minimal conflict. Positioning is mostly unique."
        return f"Multiple conflicts detected ({len(conflicts)}). Consider repositioning."


# Singleton instances
competitor_ladder_builder = CompetitorLadderBuilderTool()
differentiation_analyzer = DifferentiationAnalyzerTool()
competitor_monitoring = CompetitorMonitoringTool()
positioning_conflict_detector = PositioningConflictDetectorTool()
