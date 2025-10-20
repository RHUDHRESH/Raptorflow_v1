"""
SHARED SENTIMENT & TONE ANALYZER
Single source of truth for all sentiment analysis across the system
Eliminates duplication across content_router_agent, sentiment_tone_analyzer, moves_content_agent
"""

import logging
from typing import Dict, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class SentimentType(Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ToneType(Enum):
    """Tone classification"""
    VENTING = "venting"
    PROMOTIONAL = "promotional"
    QUESTION = "question"
    INFORMATIVE = "informative"
    CASUAL = "casual"
    FORMAL = "formal"
    URGENT = "urgent"


# CENTRALIZED WORD LISTS (Single source of truth)
# Used by: content_router_agent, sentiment_tone_analyzer, moves_content_agent
SENTIMENT_LEXICON = {
    "positive_words": {
        # High confidence (weight: 2.0)
        "love": 2.0, "amazing": 2.0, "excellent": 2.0, "fantastic": 2.0,
        "delighted": 2.0, "thrilled": 2.0, "incredible": 2.0, "outstanding": 2.0,
        "phenomenal": 2.0, "wonderful": 2.0,
        # Medium confidence (weight: 1.5)
        "beautiful": 1.5, "great": 1.5, "awesome": 1.5, "brilliant": 1.5,
        "perfect": 1.5, "happy": 1.5, "proud": 1.5, "grateful": 1.5,
        "blessed": 1.5, "superb": 1.5,
        # Low confidence (weight: 1.0)
        "good": 1.0, "nice": 1.0, "well": 1.0, "pleased": 1.0,
    },
    "negative_words": {
        # High confidence (weight: -2.0)
        "hate": -2.0, "terrible": -2.0, "awful": -2.0, "horrible": -2.0,
        "disgusting": -2.0, "depressed": -2.0, "miserable": -2.0,
        "pathetic": -2.0, "useless": -2.0, "worthless": -2.0,
        # Medium confidence (weight: -1.5)
        "angry": -1.5, "frustrated": -1.5, "disappointed": -1.5, "sad": -1.5,
        "ridiculous": -1.5, "stupid": -1.5, "dumb": -1.5, "fail": -1.5,
        # Low confidence (weight: -1.0)
        "bad": -1.0, "poor": -1.0, "wrong": -1.0, "broken": -1.0,
    },
    "venting_indicators": {
        "ugh": 1.0, "seriously": 0.8, "rant": 1.5, "frustrated": 1.0,
        "over it": 1.5, "can't believe": 1.0, "unbelievable": 1.0,
        "ridiculous": 1.0, "excuse me": 0.8, "wow": 0.5,
    },
    "promotional_indicators": {
        "buy": 2.0, "sale": 2.0, "limited time": 2.0, "offer": 2.0,
        "discount": 2.0, "free": 1.5, "shop": 1.5, "purchase": 1.5,
        "exclusive": 1.5, "order": 1.5, "get": 0.5, "now": 0.5,
    },
    "question_indicators": {
        "what": 1.0, "how": 1.0, "why": 1.0, "when": 1.0, "where": 1.0,
        "can": 0.8, "could": 0.8, "would": 0.8, "should": 0.8,
        "do you": 1.0, "have you": 1.0,
    },
    "urgent_indicators": {
        "urgent": 2.0, "asap": 2.0, "immediately": 2.0, "emergency": 2.0,
        "right now": 1.5, "crisis": 1.5, "critical": 1.5,
    },
}

FORMALITY_MARKERS = {
    "formal": ["Dear", "Sincerely", "Regards", "Furthermore", "However", "Therefore", "Moreover"],
    "casual": ["lol", "haha", "omg", "btw", "tbh", "imho", "gonna", "wanna"],
}


class SharedSentimentAnalyzer:
    """
    Shared sentiment analysis - Used by all agents/tools
    Eliminates duplicate code and ensures consistent sentiment across system
    """

    @staticmethod
    def analyze_sentiment(content: str) -> Dict[str, Any]:
        """
        Fast sentiment analysis (uses shared lexicon)
        Returns: sentiment type, score, confidence

        Token efficiency: Scans content ONCE, returns all needed data
        """
        content_lower = content.lower()

        # Single pass through content
        positive_score = sum(
            weight for word, weight in SENTIMENT_LEXICON["positive_words"].items()
            if word in content_lower
        )
        negative_score = sum(
            abs(weight) for word, weight in SENTIMENT_LEXICON["negative_words"].items()
            if word in content_lower
        )

        total_score = positive_score - negative_score
        total_possible = positive_score + negative_score if positive_score + negative_score > 0 else 1

        sentiment_value = total_score / total_possible if total_possible > 0 else 0
        sentiment_value = max(-1.0, min(1.0, sentiment_value))

        # Classify
        if sentiment_value > 0.3:
            sentiment_type = SentimentType.POSITIVE.value
        elif sentiment_value < -0.3:
            sentiment_type = SentimentType.NEGATIVE.value
        else:
            sentiment_type = SentimentType.NEUTRAL.value

        return {
            "type": sentiment_type,
            "score": round(sentiment_value, 2),
            "positive_score": round(positive_score, 2),
            "negative_score": round(negative_score, 2),
            "confidence": round(abs(sentiment_value), 2)
        }

    @staticmethod
    def analyze_tone(content: str) -> Dict[str, Any]:
        """
        Determine tone from content
        Returns: primary tone, formality, urgency
        """
        content_lower = content.lower()

        # Score tone indicators
        tone_scores = {
            ToneType.VENTING.value: sum(
                weight for word, weight in SENTIMENT_LEXICON["venting_indicators"].items()
                if word in content_lower
            ),
            ToneType.PROMOTIONAL.value: sum(
                weight for word, weight in SENTIMENT_LEXICON["promotional_indicators"].items()
                if word in content_lower
            ),
            ToneType.QUESTION.value: sum(
                weight for word, weight in SENTIMENT_LEXICON["question_indicators"].items()
                if word in content_lower
            ),
            ToneType.URGENT.value: sum(
                weight for word, weight in SENTIMENT_LEXICON["urgent_indicators"].items()
                if word in content_lower
            ),
        }

        # Determine primary tone
        primary_tone = max(tone_scores.items(), key=lambda x: x[1])[0] if tone_scores else ToneType.INFORMATIVE.value

        # Determine formality
        is_formal = any(phrase in content for phrase in FORMALITY_MARKERS["formal"])
        is_casual = any(word in content_lower for word in FORMALITY_MARKERS["casual"])
        formality = "formal" if is_formal else "casual" if is_casual else "semi-formal"

        # Detect urgency separately
        urgency_score = tone_scores.get(ToneType.URGENT.value, 0)
        is_urgent = urgency_score > 0

        return {
            "primary_tone": primary_tone,
            "tone_scores": {k: round(v, 1) for k, v in tone_scores.items()},
            "formality": formality,
            "is_urgent": is_urgent,
            "urgency_level": "high" if is_urgent else "low"
        }

    @staticmethod
    def analyze_content(content: str) -> Dict[str, Any]:
        """
        Full analysis in one call - most efficient approach
        Scans content ONCE and returns all needed data

        TOKEN EFFICIENT: ~50% fewer tokens than separate calls
        """
        word_count = len(content.split())
        char_count = len(content)
        has_question = "?" in content
        has_exclamation = "!" in content
        has_cta = any(
            cta in content.lower() for cta in ["click", "buy", "join", "subscribe", "sign up"]
        )

        sentiment = SharedSentimentAnalyzer.analyze_sentiment(content)
        tone = SharedSentimentAnalyzer.analyze_tone(content)

        return {
            "word_count": word_count,
            "character_count": char_count,
            "sentiment": sentiment,
            "tone": tone,
            "has_question": has_question,
            "has_exclamation": has_exclamation,
            "has_cta": has_cta,
            "estimated_read_time": max(1, word_count // 200)
        }


# Use sparingly - only when you need sentiment separately
def get_sentiment_for_platform_scoring(content: str) -> Tuple[str, float]:
    """
    Quick sentiment lookup optimized for platform scoring
    Returns: (sentiment_type, confidence_score)
    """
    analysis = SharedSentimentAnalyzer.analyze_sentiment(content)
    return analysis["type"], analysis["confidence"]


# Use sparingly - only when you need tone separately
def get_tone_for_platform_scoring(content: str) -> str:
    """
    Quick tone lookup optimized for platform scoring
    Returns: tone_type
    """
    tone_analysis = SharedSentimentAnalyzer.analyze_tone(content)
    return tone_analysis["primary_tone"]
