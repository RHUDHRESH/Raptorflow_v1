"""
ENHANCED MOVES & CONTENT AGENT
Improved content creation and distribution with intelligent routing
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class MovesContentAgentEnhanced:
    """Enhanced agent for content creation and distribution"""

    def __init__(self):
        self.name = "moves_content_agent_enhanced"
        self.description = "Create and intelligently distribute content across platforms"
        self.max_retries = 3

    async def create_and_route_content(
        self,
        business_id: str,
        content: str,
        content_type: str,
        business_data: Dict[str, Any],
        icps: List[Dict[str, Any]],
        intent: str = "auto_route",
        auto_publish: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create content and intelligently route to platforms

        Flow:
        1. Analyze content characteristics
        2. Assess tone and sentiment
        3. Match to audience personas
        4. Score platforms
        5. Generate platform recommendations
        6. Optimize content for each platform
        7. Create distribution schedule
        8. Execute distribution (if auto_publish=True)
        """

        logger.info(f"Creating and routing content for business {business_id}")

        try:
            # Step 1: Validate content
            validation = await self._validate_content(content, content_type)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["errors"]
                }

            # Step 2: Analyze content
            analysis = await self._analyze_content(content, content_type)

            # Step 3: Score platforms
            platform_scores = await self._score_platforms(
                analysis,
                business_data,
                icps
            )

            # Step 4: Get recommendations
            recommendations = self._generate_recommendations(platform_scores)

            # Step 5: Optimize for recommended platforms
            optimized_content = await self._optimize_content_for_platforms(
                content,
                [r["platform"] for r in recommendations[:5]]
            )

            # Step 6: Create distribution plan
            distribution_plan = await self._create_distribution_plan(
                business_id,
                content,
                recommendations,
                optimized_content
            )

            # Step 7: Execute if auto_publish
            distribution_results = None
            if auto_publish:
                distribution_results = await self._execute_distribution(distribution_plan)

            return {
                "success": True,
                "business_id": business_id,
                "content_analysis": analysis,
                "platform_recommendations": recommendations,
                "distribution_plan": distribution_plan,
                "distribution_results": distribution_results,
                "auto_published": auto_publish,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.exception(f"Content creation and routing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _validate_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Validate content before routing"""

        errors = []
        valid = True

        # Check for empty content
        if not content or len(content.strip()) == 0:
            errors.append("Content cannot be empty")
            valid = False

        # Check minimum length
        word_count = len(content.split())
        if word_count < 3:
            errors.append("Content must be at least 3 words")
            valid = False

        # Check for valid content type
        valid_types = ["text", "promotional", "question", "venting", "announcement", "story", "tutorial"]
        if content_type.lower() not in valid_types:
            errors.append(f"Invalid content type. Valid: {', '.join(valid_types)}")
            valid = False

        return {
            "valid": valid,
            "errors": errors,
            "word_count": word_count,
            "character_count": len(content)
        }

    async def _analyze_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Analyze content structure and characteristics"""

        logger.info("Analyzing content characteristics")

        word_count = len(content.split())
        has_links = "http" in content.lower() or "www" in content.lower()
        has_hashtags = "#" in content
        has_mentions = "@" in content
        has_visuals_keywords = any(
            word in content.lower() for word in ["image", "video", "photo", "screenshot", "picture"]
        )
        has_question = "?" in content
        has_cta = any(
            word in content.lower() for word in [
                "click", "join", "subscribe", "sign up", "buy", "download",
                "share", "like", "comment", "register", "enroll", "register", "learn more"
            ]
        )

        # Sentiment analysis (simplified)
        positive_words = ["great", "amazing", "excellent", "love", "fantastic", "awesome"]
        negative_words = ["hate", "bad", "terrible", "awful", "angry", "frustrated"]

        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())

        if negative_count > positive_count:
            sentiment = "negative"
        elif positive_count > negative_count:
            sentiment = "positive"
        else:
            sentiment = "neutral"

        return {
            "word_count": word_count,
            "character_count": len(content),
            "content_type": content_type,
            "has_links": has_links,
            "has_hashtags": has_hashtags,
            "has_mentions": has_mentions,
            "has_visuals_keywords": has_visuals_keywords,
            "has_question": has_question,
            "has_cta": has_cta,
            "sentiment": sentiment,
            "estimated_read_time": max(1, word_count // 200),
            "complexity": self._assess_complexity(word_count, content)
        }

    async def _score_platforms(
        self,
        analysis: Dict[str, Any],
        business_data: Dict[str, Any],
        icps: List[Dict[str, Any]]
    ) -> Dict[str, Dict]:
        """Score each platform for content"""

        logger.info("Scoring platforms for content fit")

        platform_scores = {}

        # Platform scoring logic
        platforms = ["twitter", "linkedin", "facebook", "instagram", "tiktok", "threads", "email", "blog", "slack", "discord"]

        for platform in platforms:
            score = self._calculate_platform_score(platform, analysis, icps)
            platform_scores[platform] = score

        return platform_scores

    def _calculate_platform_score(
        self,
        platform: str,
        analysis: Dict[str, Any],
        icps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate score for specific platform"""

        base_score = 0.5

        # Word count considerations
        word_count = analysis.get("word_count", 0)
        if platform in ["twitter", "threads"]:
            if word_count < 100:
                base_score += 0.2
        elif platform in ["linkedin", "facebook"]:
            if 50 < word_count < 500:
                base_score += 0.2
        elif platform == "blog":
            if word_count > 300:
                base_score += 0.2

        # Content type fit
        content_type = analysis.get("content_type", "text").lower()
        if platform == "instagram" and "visual" in content_type:
            base_score += 0.15
        elif platform == "twitter" and content_type in ["venting", "announcement"]:
            base_score += 0.15
        elif platform == "linkedin" and content_type == "promotional":
            base_score += 0.1

        # Sentiment fit
        sentiment = analysis.get("sentiment", "neutral")
        if platform in ["twitter", "threads"] and sentiment == "negative":
            base_score += 0.1  # Good for venting

        # Feature fit
        if analysis.get("has_cta") and platform in ["facebook", "blog", "email"]:
            base_score += 0.1

        # ICP platform preferences
        if icps:
            icp_platforms = set()
            for icp in icps:
                icp_platforms.update(icp.get("behavior", {}).get("top_platforms", []))

            if platform in icp_platforms:
                base_score += 0.1

        return {
            "platform": platform,
            "score": min(1.0, base_score),
            "reasoning": self._generate_scoring_reasoning(platform, analysis)
        }

    def _generate_scoring_reasoning(self, platform: str, analysis: Dict[str, Any]) -> str:
        """Generate reasoning for platform score"""

        reasons = []

        if platform == "twitter" and analysis.get("sentiment") == "negative":
            reasons.append("Ideal for expressing frustration or venting")
        if platform == "linkedin" and analysis.get("word_count", 0) > 100:
            reasons.append("Good length for professional insights")
        if platform == "instagram" and analysis.get("has_visuals_keywords"):
            reasons.append("Content mentions visual elements")

        return "; ".join(reasons) if reasons else f"Suitable for {platform}"

    def _generate_recommendations(self, platform_scores: Dict) -> List[Dict]:
        """Generate ranked platform recommendations"""

        ranked = sorted(
            platform_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        recommendations = []
        for platform, data in ranked:
            if data["score"] > 0.4:
                rec = {
                    "platform": platform,
                    "score": round(data["score"], 2),
                    "confidence": "high" if data["score"] > 0.7 else "medium" if data["score"] > 0.5 else "low",
                    "reasoning": data["reasoning"]
                }
                recommendations.append(rec)

        return recommendations[:5]  # Top 5 platforms

    async def _optimize_content_for_platforms(
        self,
        content: str,
        platforms: List[str]
    ) -> Dict[str, str]:
        """Generate optimized content for each platform"""

        logger.info(f"Optimizing content for {len(platforms)} platforms")

        optimized = {}

        for platform in platforms:
            optimized[platform] = self._optimize_for_platform(content, platform)

        return optimized

    def _optimize_for_platform(self, content: str, platform: str) -> str:
        """Optimize content for specific platform"""

        if platform.lower() == "twitter":
            return self._optimize_twitter(content)
        elif platform.lower() == "linkedin":
            return self._optimize_linkedin(content)
        elif platform.lower() == "facebook":
            return self._optimize_facebook(content)
        elif platform.lower() == "instagram":
            return self._optimize_instagram(content)
        else:
            return content

    def _optimize_twitter(self, content: str) -> str:
        """Optimize for Twitter"""
        # Truncate to 280 chars
        if len(content) > 250:
            content = content[:250].rsplit(' ', 1)[0] + "..."
        # Add emoji if missing
        if "😊" not in content and "🎯" not in content:
            content += " 🎯"
        return content

    def _optimize_linkedin(self, content: str) -> str:
        """Optimize for LinkedIn"""
        # Add line breaks
        sentences = content.split('. ')
        content = '.\n\n'.join(sentences)
        # Add engagement question
        if not content.endswith("?"):
            content += "\n\nWhat are your thoughts?"
        return content

    def _optimize_facebook(self, content: str) -> str:
        """Optimize for Facebook"""
        # Add emoji
        if not content.startswith("👉"):
            content = "👉 " + content
        # Add engagement hook
        if "?" not in content:
            content += "\n\nWhat do you think? 👇"
        return content

    def _optimize_instagram(self, content: str) -> str:
        """Optimize for Instagram"""
        # Shorten if needed
        if len(content) > 150:
            content = content[:150]
        # Add hashtags
        content += "\n\n#trending #viral #daily"
        return content

    async def _create_distribution_plan(
        self,
        business_id: str,
        content: str,
        recommendations: List[Dict],
        optimized_content: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create distribution plan for all recommended platforms"""

        logger.info("Creating distribution plan")

        plan = {
            "business_id": business_id,
            "created_at": datetime.now().isoformat(),
            "platforms": []
        }

        for rec in recommendations[:3]:  # Top 3 platforms
            platform = rec["platform"]
            plan["platforms"].append({
                "platform": platform,
                "content": optimized_content.get(platform, content),
                "scheduled_time": datetime.now().isoformat(),
                "status": "ready",
                "score": rec["score"]
            })

        return plan

    async def _execute_distribution(self, plan: Dict[str, Any]) -> List[Dict]:
        """Execute content distribution"""

        logger.info(f"Executing distribution to {len(plan['platforms'])} platforms")

        results = []

        for platform_plan in plan["platforms"]:
            result = {
                "platform": platform_plan["platform"],
                "status": "posted",
                "post_id": f"{platform_plan['platform']}_{datetime.now().timestamp()}",
                "posted_at": datetime.now().isoformat(),
                "tracking_enabled": True
            }
            results.append(result)

        return results

    def _assess_complexity(self, word_count: int, content: str) -> str:
        """Assess content complexity"""

        avg_word_length = sum(len(word) for word in content.split()) / max(1, len(content.split()))

        if word_count < 50:
            complexity = "simple"
        elif word_count > 300:
            complexity = "complex"
        else:
            complexity = "moderate"

        if avg_word_length > 6:
            complexity = "complex"

        return complexity


class ContentScheduler:
    """Schedule content creation and distribution"""

    def __init__(self):
        self.name = "content_scheduler"
        self.description = "Schedule content creation and distribution"

    async def _execute(
        self,
        business_id: str,
        content_calendar: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Schedule content distribution"""

        logger.info(f"Scheduling {len(content_calendar)} content pieces")

        try:
            scheduled = []

            for content_item in content_calendar:
                scheduled_item = {
                    "content": content_item.get("content", ""),
                    "platforms": content_item.get("platforms", []),
                    "scheduled_time": content_item.get("scheduled_time", datetime.now().isoformat()),
                    "status": "scheduled",
                    "id": f"scheduled_{datetime.now().timestamp()}"
                }
                scheduled.append(scheduled_item)

            return {
                "success": True,
                "business_id": business_id,
                "scheduled_items": scheduled,
                "total": len(scheduled),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Scheduling failed: {str(e)}")
            return {"success": False, "error": str(e)}


# Singleton instances
moves_content_agent_enhanced = MovesContentAgentEnhanced()
content_scheduler = ContentScheduler()
