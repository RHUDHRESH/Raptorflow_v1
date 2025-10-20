"""
CONTENT ROUTER AGENT v1
Intelligently routes content to optimal platforms based on tone, message, audience

Analyzes:
- Content sentiment and tone
- Message type and intent
- Target audience preferences
- Platform-audience fit
- Engagement potential
- Risk assessment

Recommends best platforms for distribution
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ContentRouterAgent:
    """Intelligent content routing to optimal platforms"""

    def __init__(self):
        self.name = "content_router_agent"
        self.description = "Route content to optimal platforms"

    async def analyze_and_route(
        self,
        business_id: str,
        content: str,
        content_type: str,
        business_data: Dict[str, Any],
        icps: List[Dict[str, Any]],
        additional_context: Dict = None
    ) -> Dict[str, Any]:
        """
        Analyze content and recommend optimal platforms

        Flow:
        1. Analyze content tone and sentiment
        2. Extract message intent and type
        3. Get target audience preferences
        4. Score each platform
        5. Generate platform recommendations
        6. Provide optimization suggestions
        """

        logger.info(f"Routing content for business {business_id}")

        try:
            # Step 1: Analyze Content
            analysis = await self._analyze_content(content, content_type)

            # Step 2: Assess Tone and Sentiment
            tone_assessment = self._assess_tone(analysis, content)

            # Step 3: Analyze Audience Match
            audience_match = self._analyze_audience_match(analysis, icps)

            # Step 4: Score Platforms
            platform_scores = await self._score_platforms(
                analysis,
                tone_assessment,
                audience_match,
                business_data
            )

            # Step 5: Generate Recommendations
            recommendations = self._generate_recommendations(
                platform_scores,
                analysis,
                content
            )

            # Step 6: Risk Assessment
            risks = self._assess_risks(analysis, content)

            return {
                "success": True,
                "business_id": business_id,
                "content_analysis": analysis,
                "tone_assessment": tone_assessment,
                "audience_match": audience_match,
                "platform_scores": platform_scores,
                "recommendations": recommendations,
                "risks": risks,
                "primary_platforms": [r["platform"] for r in recommendations[:3]],
                "routing_confidence": round(recommendations[0]["confidence"], 2) if recommendations else 0,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.exception(f"Routing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _analyze_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Analyze content structure and intent"""
        logger.info(f"Analyzing {content_type} content")

        # Extract content characteristics
        word_count = len(content.split())
        has_links = "http" in content.lower() or "www" in content.lower()
        has_hashtags = "#" in content
        has_mentions = "@" in content
        has_visuals = any(word in content.lower() for word in ["image", "video", "photo", "screenshot"])
        has_question = "?" in content
        has_call_to_action = any(word in content.lower() for word in [
            "click", "join", "subscribe", "sign up", "buy", "download",
            "share", "like", "comment", "register", "enroll"
        ])

        return {
            "word_count": word_count,
            "character_count": len(content),
            "content_type": content_type,
            "has_links": has_links,
            "has_hashtags": has_hashtags,
            "has_mentions": has_mentions,
            "has_visuals": has_visuals,
            "has_question": has_question,
            "has_cta": has_call_to_action,
            "estimated_read_time": max(1, word_count // 200),
            "content_preview": content[:100] + "..." if len(content) > 100 else content
        }

    def _assess_tone(self, analysis: Dict, content: str) -> Dict[str, Any]:
        """Assess tone and sentiment"""
        content_lower = content.lower()

        # Sentiment detection
        positive_words = ["great", "excellent", "amazing", "awesome", "love", "fantastic",
                         "beautiful", "perfect", "wonderful", "brilliant"]
        negative_words = ["hate", "bad", "terrible", "awful", "angry", "frustrated",
                         "disappointed", "stupid", "ridiculous", "disgusted"]
        question_words = ["how", "what", "why", "when", "where", "can", "could", "would"]

        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        question_count = sum(1 for word in question_words if word in content_lower)

        # Determine sentiment
        if negative_count > positive_count:
            sentiment = "negative"
            tone = "venting"
        elif positive_count > negative_count:
            sentiment = "positive"
            tone = "promotional"
        elif question_count > 0:
            sentiment = "neutral"
            tone = "question"
        else:
            sentiment = "neutral"
            tone = "informative"

        # Formality level
        is_formal = any(phrase in content for phrase in [
            "Dear", "Sincerely", "Regards", "Furthermore", "However"
        ])
        is_casual = any(word in content_lower for word in ["lol", "haha", "omg", "btw", "tbh"])

        formality = "formal" if is_formal else "casual" if is_casual else "semi-formal"

        return {
            "sentiment": sentiment,
            "tone": tone,
            "formality": formality,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "engagement_potential": "high" if (positive_count > 0 or question_count > 0) else "medium"
        }

    def _analyze_audience_match(self, analysis: Dict, icps: List[Dict]) -> Dict[str, Any]:
        """Analyze content-audience fit"""
        if not icps:
            return {"primary_audience": "general", "platforms": []}

        audiences = {}

        for icp in icps:
            name = icp.get("name", "Unknown")
            platforms = icp.get("behavior", {}).get("top_platforms", [])

            audiences[name] = {
                "fit_score": self._calculate_audience_fit(analysis, icp),
                "platforms": platforms,
                "demographics": icp.get("demographics", {}),
                "content_preferences": icp.get("behavior", {}).get("content_preferences", {})
            }

        # Sort by fit
        sorted_audiences = sorted(audiences.items(), key=lambda x: x[1]["fit_score"], reverse=True)

        return {
            "primary_audience": sorted_audiences[0][0] if sorted_audiences else "general",
            "audience_scores": {name: score["fit_score"] for name, score in sorted_audiences},
            "audiences": audiences
        }

    def _calculate_audience_fit(self, analysis: Dict, icp: Dict) -> float:
        """Calculate how well content fits ICP"""
        score = 0.5  # Base score

        # Word count fit
        word_count = analysis.get("word_count", 0)
        if 50 < word_count < 500:  # Sweet spot
            score += 0.2
        elif 30 < word_count < 1000:
            score += 0.1

        # Question fit
        if analysis.get("has_question"):
            score += 0.1

        # CTA fit
        if analysis.get("has_cta"):
            score += 0.1

        return min(1.0, score)

    async def _score_platforms(
        self,
        analysis: Dict,
        tone_assessment: Dict,
        audience_match: Dict,
        business_data: Dict
    ) -> Dict[str, Dict]:
        """Score each platform for this content"""

        platforms = {
            "twitter": self._score_twitter(analysis, tone_assessment),
            "linkedin": self._score_linkedin(analysis, tone_assessment),
            "facebook": self._score_facebook(analysis, tone_assessment),
            "instagram": self._score_instagram(analysis, tone_assessment),
            "tiktok": self._score_tiktok(analysis, tone_assessment),
            "threads": self._score_threads(analysis, tone_assessment),
            "email": self._score_email(analysis, tone_assessment),
            "blog": self._score_blog(analysis, tone_assessment),
            "slack": self._score_slack(analysis, tone_assessment),
            "discord": self._score_discord(analysis, tone_assessment),
        }

        return platforms

    def _score_twitter(self, analysis: Dict, tone: Dict) -> Dict:
        """Score Twitter fit"""
        score = 0.5

        if analysis.get("word_count", 0) < 300:
            score += 0.2
        if tone.get("sentiment") in ["positive", "negative"]:
            score += 0.1
        if analysis.get("has_hashtags"):
            score += 0.1
        if tone.get("engagement_potential") == "high":
            score += 0.15

        if tone.get("tone") == "venting":
            score += 0.25  # Twitter is perfect for venting!

        return {
            "platform": "Twitter/X",
            "score": min(1.0, score),
            "reasoning": f"{tone.get('tone')} content is great for Twitter",
            "character_limit": 280,
            "best_for": ["Venting", "Breaking news", "Quick reactions"],
            "formatting_tips": ["Use hashtags", "Thread for longer content", "Emojis encouraged"]
        }

    def _score_linkedin(self, analysis: Dict, tone: Dict) -> Dict:
        """Score LinkedIn fit"""
        score = 0.4

        if analysis.get("word_count", 0) > 100:
            score += 0.2
        if tone.get("formality") in ["formal", "semi-formal"]:
            score += 0.2
        if tone.get("tone") in ["informative", "promotional"]:
            score += 0.15
        if tone.get("sentiment") == "positive":
            score += 0.1

        if tone.get("tone") == "venting":
            score -= 0.3  # LinkedIn not ideal for complaints

        return {
            "platform": "LinkedIn",
            "score": max(0.0, min(1.0, score)),
            "reasoning": "Professional network for thought leadership",
            "character_limit": 3000,
            "best_for": ["Industry insights", "Professional updates", "Thought leadership"],
            "formatting_tips": ["Line breaks for readability", "Professional tone", "Link to article"]
        }

    def _score_facebook(self, analysis: Dict, tone: Dict) -> Dict:
        """Score Facebook fit"""
        score = 0.5

        if analysis.get("word_count", 0) < 200:
            score += 0.15
        if tone.get("sentiment") in ["positive", "neutral"]:
            score += 0.15
        if analysis.get("has_visuals"):
            score += 0.2

        if tone.get("tone") == "venting":
            score += 0.2  # Facebook allows venting with broader audience

        return {
            "platform": "Facebook",
            "score": min(1.0, score),
            "reasoning": "Wide reach across demographics",
            "character_limit": 63206,
            "best_for": ["Community updates", "Visual content", "Broader reach"],
            "formatting_tips": ["Add image", "Encourage comments", "Use community groups"]
        }

    def _score_instagram(self, analysis: Dict, tone: Dict) -> Dict:
        """Score Instagram fit"""
        score = 0.3

        if analysis.get("has_visuals"):
            score += 0.4
        if analysis.get("word_count", 0) < 150:
            score += 0.15
        if tone.get("sentiment") == "positive":
            score += 0.1
        if analysis.get("has_hashtags"):
            score += 0.05

        if tone.get("tone") == "venting":
            score -= 0.2  # Instagram is for aesthetics

        return {
            "platform": "Instagram",
            "score": max(0.0, min(1.0, score)),
            "reasoning": "Visual-first platform, best with images",
            "character_limit": 2200,
            "best_for": ["Visual stories", "Lifestyle content", "Community building"],
            "formatting_tips": ["High-quality image required", "Use hashtags", "Tell a story"]
        }

    def _score_tiktok(self, analysis: Dict, tone: Dict) -> Dict:
        """Score TikTok fit"""
        score = 0.4

        if analysis.get("has_visuals"):
            score += 0.25
        if tone.get("tone") in ["casual", "funny"]:
            score += 0.2
        if analysis.get("word_count", 0) < 100:
            score += 0.15

        if tone.get("tone") == "venting":
            score += 0.15  # TikTok allows authentic, emotional content

        return {
            "platform": "TikTok",
            "score": min(1.0, score),
            "reasoning": "Short-form video, authentic content performs well",
            "character_limit": 2500,
            "best_for": ["Authentic moments", "Casual content", "Behind-the-scenes"],
            "formatting_tips": ["Video format", "Use trending sounds", "Hook in first 3 seconds"]
        }

    def _score_threads(self, analysis: Dict, tone: Dict) -> Dict:
        """Score Threads fit"""
        score = 0.55

        if tone.get("sentiment") in ["positive", "negative"]:
            score += 0.15
        if analysis.get("word_count", 0) < 500:
            score += 0.15

        if tone.get("tone") == "venting":
            score += 0.25  # Threads is great for conversations and venting

        return {
            "platform": "Threads",
            "score": min(1.0, score),
            "reasoning": "Twitter alternative, similar audience",
            "character_limit": 500,
            "best_for": ["Venting", "Conversations", "Nuanced takes"],
            "formatting_tips": ["Thread format encouraged", "Conversational tone", "Emojis work"]
        }

    def _score_email(self, analysis: Dict, tone: Dict) -> Dict:
        """Score Email fit"""
        score = 0.4

        if analysis.get("word_count", 0) > 100:
            score += 0.2
        if tone.get("formality") in ["formal", "semi-formal"]:
            score += 0.2
        if analysis.get("has_cta"):
            score += 0.2

        if tone.get("tone") == "venting":
            score -= 0.25  # Email not ideal for venting

        return {
            "platform": "Email",
            "score": max(0.0, min(1.0, score)),
            "reasoning": "Direct communication with subscribers",
            "character_limit": "Unlimited",
            "best_for": ["Announcements", "Newsletters", "Direct communication"],
            "formatting_tips": ["Clear subject line", "Scannable format", "CTA button"]
        }

    def _score_blog(self, analysis: Dict, tone: Dict) -> Dict:
        """Score Blog fit"""
        score = 0.3

        if analysis.get("word_count", 0) > 300:
            score += 0.3
        if tone.get("tone") in ["informative", "promotional"]:
            score += 0.25
        if tone.get("sentiment") == "positive":
            score += 0.15

        if tone.get("tone") == "venting":
            score -= 0.3  # Blog is for long-form, not venting

        return {
            "platform": "Blog",
            "score": max(0.0, min(1.0, score)),
            "reasoning": "Long-form content for SEO and thought leadership",
            "character_limit": "Unlimited",
            "best_for": ["Deep dives", "SEO", "Portfolio"],
            "formatting_tips": ["Outline first", "Add images", "Internal links"]
        }

    def _score_slack(self, analysis: Dict, tone: Dict) -> Dict:
        """Score Slack fit"""
        score = 0.4

        if analysis.get("word_count", 0) < 200:
            score += 0.2
        if tone.get("formality") == "casual":
            score += 0.2
        if tone.get("tone") in ["question", "venting"]:
            score += 0.15

        return {
            "platform": "Slack",
            "score": min(1.0, score),
            "reasoning": "Great for team communication and venting",
            "character_limit": "Unlimited",
            "best_for": ["Team updates", "Questions", "Discussions"],
            "formatting_tips": ["Thread replies", "Use emojis", "Tag relevant people"]
        }

    def _score_discord(self, analysis: Dict, tone: Dict) -> Dict:
        """Score Discord fit"""
        score = 0.35

        if tone.get("formality") == "casual":
            score += 0.25
        if tone.get("tone") in ["venting", "question"]:
            score += 0.2
        if analysis.get("word_count", 0) < 300:
            score += 0.2

        return {
            "platform": "Discord",
            "score": min(1.0, score),
            "reasoning": "Community platform for casual conversation",
            "character_limit": 2000,
            "best_for": ["Community chat", "Venting", "Real-time discussion"],
            "formatting_tips": ["Code blocks for formatting", "Threads for discussions", "Emojis"]
        }

    def _generate_recommendations(
        self,
        platform_scores: Dict,
        analysis: Dict,
        content: str
    ) -> List[Dict]:
        """Generate ranked platform recommendations"""

        # Sort platforms by score
        ranked = sorted(
            [(name, data) for name, data in platform_scores.items()],
            key=lambda x: x[1]["score"],
            reverse=True
        )

        recommendations = []

        for platform, data in ranked:
            rec = {
                "platform": data["platform"],
                "score": data["score"],
                "confidence": round(data["score"], 2),
                "reasoning": data["reasoning"],
                "best_for": data["best_for"],
                "tips": data["formatting_tips"],
                "character_limit": data["character_limit"],
                "recommendation": "Highly Recommended" if data["score"] > 0.7 else "Recommended" if data["score"] > 0.5 else "Consider"
            }
            recommendations.append(rec)

        return recommendations

    def _assess_risks(self, analysis: Dict, content: str) -> List[Dict]:
        """Assess risks of posting content"""
        risks = []

        # Check for controversial words
        controversial = ["hate", "kill", "attack", "destroy", "ban"]
        if any(word in content.lower() for word in controversial):
            risks.append({
                "type": "potentially_controversial",
                "severity": "medium",
                "message": "Content may be flagged as controversial on some platforms",
                "recommendation": "Review moderation policies before posting"
            })

        # Check for all caps (yelling)
        all_caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        if all_caps_ratio > 0.5:
            risks.append({
                "type": "excessive_caps",
                "severity": "low",
                "message": "Content has excessive capitalization",
                "recommendation": "Reduce all-caps for better tone"
            })

        # Check for personal information
        if any(word in content.lower() for word in ["password", "credit card", "social security", "private"]):
            risks.append({
                "type": "sensitive_data",
                "severity": "high",
                "message": "Content contains potentially sensitive information",
                "recommendation": "Remove sensitive data before posting"
            })

        return risks


# Singleton instance
content_router = ContentRouterAgent()
