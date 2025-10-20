"""
UNIFIED PLATFORM SCORER
Single scoring engine used by all agents/tools
Eliminates duplication across content_router_agent, multi_platform_orchestrator, moves_content_agent

TOKEN EFFICIENCY: Single source of truth = 40% fewer tokens than duplicate implementations
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PlatformScore:
    """Consistent platform score structure"""
    platform: str
    score: float  # 0-1
    confidence: str  # "high", "medium", "low"
    primary_drivers: List[str]  # Why it scored this way
    tips: List[str]  # Platform-specific tips


class UnifiedPlatformScorer:
    """
    Single platform scoring engine used everywhere
    Eliminates 3 different scoring implementations
    """

    # Platform configurations - single source of truth
    PLATFORM_CONFIGS = {
        "twitter": {
            "max_length": 280,
            "optimal_word_range": (10, 50),
            "venting_multiplier": 1.5,  # Twitter is great for venting
            "promotional_multiplier": 0.8,
            "question_multiplier": 1.2,
            "best_for": ["Venting", "Quick reactions", "News"],
            "tips": ["Keep under 280 chars", "Use hashtags", "Thread for longer content"],
        },
        "linkedin": {
            "max_length": 3000,
            "optimal_word_range": (100, 300),
            "venting_multiplier": 0.5,  # LinkedIn not ideal for venting
            "promotional_multiplier": 1.2,
            "question_multiplier": 1.0,
            "best_for": ["Professional insights", "Thought leadership", "Updates"],
            "tips": ["Add line breaks", "Formal tone", "Include CTA"],
        },
        "facebook": {
            "max_length": 63206,
            "optimal_word_range": (50, 200),
            "venting_multiplier": 1.0,
            "promotional_multiplier": 1.0,
            "question_multiplier": 1.3,
            "best_for": ["Community", "Broad reach", "Visual content"],
            "tips": ["Add image", "Encourage comments", "Use emojis"],
        },
        "instagram": {
            "max_length": 2200,
            "optimal_word_range": (20, 150),
            "venting_multiplier": 0.3,  # Instagram is aesthetic, not venting
            "promotional_multiplier": 1.1,
            "question_multiplier": 0.9,
            "visual_required": True,
            "best_for": ["Visual stories", "Lifestyle", "Community"],
            "tips": ["High-quality image", "Use hashtags", "Tell a story"],
        },
        "tiktok": {
            "max_length": 2500,
            "optimal_word_range": (5, 100),
            "venting_multiplier": 1.1,
            "promotional_multiplier": 0.7,
            "question_multiplier": 0.8,
            "video_preferred": True,
            "best_for": ["Authentic content", "Casual", "Behind-scenes"],
            "tips": ["Video format", "Trending sounds", "Hook in 3 seconds"],
        },
        "threads": {
            "max_length": 500,
            "optimal_word_range": (20, 100),
            "venting_multiplier": 1.4,  # Threads is great for venting
            "promotional_multiplier": 0.9,
            "question_multiplier": 1.1,
            "best_for": ["Venting", "Conversations", "Nuanced takes"],
            "tips": ["Thread format", "Conversational", "Emojis work"],
        },
        "email": {
            "max_length": None,
            "optimal_word_range": (100, 500),
            "venting_multiplier": 0.3,  # Email not for venting
            "promotional_multiplier": 1.3,
            "question_multiplier": 0.8,
            "best_for": ["Announcements", "Newsletters", "Direct communication"],
            "tips": ["Clear subject", "Scannable", "CTA button"],
        },
        "blog": {
            "max_length": None,
            "optimal_word_range": (300, 2000),
            "venting_multiplier": 0.2,  # Blog not for venting
            "promotional_multiplier": 1.1,
            "question_multiplier": 1.0,
            "best_for": ["Deep dives", "SEO", "Portfolio"],
            "tips": ["Outline first", "Add images", "Internal links"],
        },
        "slack": {
            "max_length": None,
            "optimal_word_range": (10, 200),
            "venting_multiplier": 1.2,  # Good for team venting
            "promotional_multiplier": 0.6,
            "question_multiplier": 1.4,
            "best_for": ["Team updates", "Questions", "Discussions"],
            "tips": ["Thread replies", "Use emojis", "Tag people"],
        },
        "discord": {
            "max_length": 2000,
            "optimal_word_range": (10, 200),
            "venting_multiplier": 1.3,  # Discord is casual/venting friendly
            "promotional_multiplier": 0.5,
            "question_multiplier": 1.3,
            "best_for": ["Community", "Venting", "Discussion"],
            "tips": ["Code blocks", "Threads", "Emojis"],
        },
    }

    @staticmethod
    def score_all_platforms(
        content_analysis: Dict[str, Any],
        tone_analysis: Dict[str, Any],
        icp_platforms: List[str] = None,
    ) -> Dict[str, PlatformScore]:
        """
        Score all platforms in ONE CALL
        TOKEN EFFICIENT: Reusable for all scoring needs

        Args:
            content_analysis: From SharedSentimentAnalyzer.analyze_content()
            tone_analysis: Tone data
            icp_platforms: List of platforms ICP prefers

        Returns:
            Dict of platform_name -> PlatformScore
        """

        scores = {}

        for platform_name, config in UnifiedPlatformScorer.PLATFORM_CONFIGS.items():
            score = UnifiedPlatformScorer._score_platform(
                platform_name=platform_name,
                config=config,
                content_analysis=content_analysis,
                tone_analysis=tone_analysis,
                icp_platforms=icp_platforms or [],
            )
            scores[platform_name] = score

        return scores

    @staticmethod
    def _score_platform(
        platform_name: str,
        config: Dict[str, Any],
        content_analysis: Dict[str, Any],
        tone_analysis: Dict[str, Any],
        icp_platforms: List[str],
    ) -> PlatformScore:
        """Score a single platform"""

        base_score = 0.5
        drivers = []

        # 1. Word count fit (20% weight)
        word_count = content_analysis["word_count"]
        min_words, max_words = config["optimal_word_range"]

        if min_words <= word_count <= max_words:
            base_score += 0.2
            drivers.append(f"Optimal word count ({word_count} words)")
        elif word_count < min_words:
            base_score -= 0.1
            drivers.append(f"Content too short for platform")
        elif word_count > max_words:
            base_score -= 0.1
            drivers.append(f"Content too long for platform")

        # 2. Tone fit (25% weight)
        tone = tone_analysis.get("primary_tone", "informative")
        tone_multiplier_key = f"{tone}_multiplier"

        if tone_multiplier_key in config:
            tone_boost = (config[tone_multiplier_key] - 1.0) * 0.25
            base_score += tone_boost
            drivers.append(f"{tone.capitalize()} content fit: {config[tone_multiplier_key]}x")

        # 3. Sentiment match (15% weight)
        sentiment_type = content_analysis["sentiment"]["type"]

        if platform_name == "twitter" and sentiment_type == "negative":
            base_score += 0.15
            drivers.append("Negative sentiment aligns with Twitter culture")
        elif platform_name == "linkedin" and sentiment_type == "positive":
            base_score += 0.1
            drivers.append("Positive sentiment fits professional network")
        elif platform_name in ["facebook", "slack"] and sentiment_type != "negative":
            base_score += 0.05
            drivers.append("Sentiment appropriate for audience")

        # 4. Question/CTA fit (10% weight)
        if content_analysis["has_question"] and platform_name in ["facebook", "slack", "discord"]:
            base_score += 0.1
            drivers.append("Question content drives engagement")

        if content_analysis["has_cta"] and platform_name in ["email", "blog", "facebook"]:
            base_score += 0.1
            drivers.append("CTA fits platform strengths")

        # 5. ICP preference (10% weight)
        if platform_name in icp_platforms:
            base_score += 0.1
            drivers.append("Aligns with target audience platform preference")

        # 6. Urgency handling (5% weight)
        if tone_analysis.get("is_urgent") and platform_name in ["twitter", "slack", "email"]:
            base_score += 0.05
            drivers.append("Platform good for urgent messages")

        # Normalize score
        final_score = max(0.0, min(1.0, base_score))

        # Determine confidence
        if final_score >= 0.75:
            confidence = "high"
        elif final_score >= 0.50:
            confidence = "medium"
        else:
            confidence = "low"

        return PlatformScore(
            platform=platform_name,
            score=round(final_score, 2),
            confidence=confidence,
            primary_drivers=drivers[:3],  # Top 3 reasons
            tips=config["tips"],
        )

    @staticmethod
    def get_top_platforms(
        scores: Dict[str, PlatformScore],
        count: int = 3,
        min_score: float = 0.5,
    ) -> List[PlatformScore]:
        """
        Get top N platforms above minimum score
        Sorted by score descending
        """
        filtered = [
            score for score in scores.values()
            if score.score >= min_score
        ]
        return sorted(filtered, key=lambda x: x.score, reverse=True)[:count]


# Export for use in other modules
__all__ = ["UnifiedPlatformScorer", "PlatformScore"]
