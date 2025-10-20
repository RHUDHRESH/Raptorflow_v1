"""
PLATFORM RECOMMENDATION TOOLS
Generate platform-specific content optimization and recommendations
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PlatformRecommendationTool:
    """Generate platform-specific recommendations"""

    def __init__(self):
        self.name = "platform_recommendation"
        self.description = "Generate platform-specific content recommendations"

    async def _execute(
        self,
        platform: str,
        content_analysis: Dict[str, Any],
        tone_assessment: Dict[str, Any],
        audience_match: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate recommendations for specific platform"""

        logger.info(f"Generating recommendations for {platform}")

        try:
            if platform.lower() == "twitter":
                recommendations = self._recommend_twitter(content_analysis, tone_assessment)
            elif platform.lower() == "linkedin":
                recommendations = self._recommend_linkedin(content_analysis, tone_assessment)
            elif platform.lower() == "facebook":
                recommendations = self._recommend_facebook(content_analysis, tone_assessment)
            elif platform.lower() == "instagram":
                recommendations = self._recommend_instagram(content_analysis, tone_assessment)
            elif platform.lower() == "tiktok":
                recommendations = self._recommend_tiktok(content_analysis, tone_assessment)
            elif platform.lower() == "email":
                recommendations = self._recommend_email(content_analysis, tone_assessment)
            elif platform.lower() == "blog":
                recommendations = self._recommend_blog(content_analysis, tone_assessment)
            else:
                recommendations = self._recommend_generic(platform, content_analysis, tone_assessment)

            return {
                "success": True,
                "platform": platform,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _recommend_twitter(self, analysis: Dict, tone: Dict) -> Dict[str, Any]:
        """Twitter-specific recommendations"""
        return {
            "platform": "Twitter/X",
            "primary_strategy": "Real-time engagement and venting",
            "character_limit": 280,
            "posting_frequency": "3-5 times daily",
            "optimal_posting_times": ["8-10 AM", "12-1 PM", "5-7 PM"],
            "content_guidelines": [
                "Keep under 280 characters for single posts",
                "Use 1-2 hashtags maximum",
                "Thread if content exceeds character limit",
                f"Your content: {analysis.get('word_count', 0)} words - {'Use thread' if analysis.get('word_count', 0) > 50 else 'Perfect for single post'}"
            ],
            "best_practices": [
                f"Sentiment ({tone.get('sentiment')}): {'Lean into emotion' if tone.get('tone') == 'venting' else 'Stay balanced'}",
                "Include call-to-action or question for engagement",
                "Add relevant hashtags for discoverability",
                "Use emojis to add personality"
            ],
            "formatting_suggestions": {
                "use_hashtags": analysis.get("has_hashtags", False),
                "add_thread_format": analysis.get("word_count", 0) > 50,
                "include_emojis": tone.get("formality") == "casual",
                "add_link": analysis.get("has_links", False)
            },
            "engagement_tactics": [
                "Ask a question to drive replies",
                "Share controversial takes (if appropriate)",
                "Respond to replies within 1 hour",
                "Quote tweet to start conversations"
            ]
        }

    def _recommend_linkedin(self, analysis: Dict, tone: Dict) -> Dict[str, Any]:
        """LinkedIn-specific recommendations"""
        return {
            "platform": "LinkedIn",
            "primary_strategy": "Professional thought leadership",
            "character_limit": 3000,
            "posting_frequency": "2-3 times weekly",
            "optimal_posting_times": ["8-10 AM Tuesday-Thursday"],
            "content_guidelines": [
                "Aim for 100-300 words for optimal engagement",
                "Add line breaks for readability",
                f"Your content: {analysis.get('word_count', 0)} words - {'Expand with context' if analysis.get('word_count', 0) < 100 else 'Good length'}",
                "Start with a hook in first 2 lines"
            ],
            "best_practices": [
                f"Tone ({tone.get('tone')}): {'Soften venting tone' if tone.get('tone') == 'venting' else 'Perfect'}",
                "Share professional insights or lessons learned",
                "Include call-to-action (connect, comment, share)",
                "Tag relevant people and companies (max 5)",
                "Use line breaks for visual scannability"
            ],
            "formatting_suggestions": {
                "add_line_breaks": True,
                "bold_key_points": True,
                "include_hashtags": 3,
                "add_link": analysis.get("has_links", False),
                "remove_casual_language": tone.get("formality") != "formal"
            },
            "engagement_tactics": [
                "Engage with comments within 24 hours",
                "Share industry insights or personal learnings",
                "Ask for advice or perspectives",
                "Tag 3-5 relevant connections",
                "Follow up with direct messages to engaged users"
            ]
        }

    def _recommend_facebook(self, analysis: Dict, tone: Dict) -> Dict[str, Any]:
        """Facebook-specific recommendations"""
        return {
            "platform": "Facebook",
            "primary_strategy": "Community engagement and storytelling",
            "character_limit": 63206,
            "posting_frequency": "1-2 times daily",
            "optimal_posting_times": ["1-3 PM", "7-9 PM"],
            "content_guidelines": [
                "100-200 words is sweet spot",
                f"Your content: {analysis.get('word_count', 0)} words - {'Add context' if analysis.get('word_count', 0) < 50 else 'Good length'}",
                "Always add an image or video",
                f"Visuals detected: {'Yes, good!' if analysis.get('has_visuals') else 'Add image for better engagement'}"
            ],
            "best_practices": [
                f"Tone ({tone.get('tone')}): Conversational and relatable",
                "Ask questions to encourage comments",
                "Use emojis to add personality",
                "Create emotional connection",
                "Encourage shares and tags"
            ],
            "formatting_suggestions": {
                "add_image": not analysis.get("has_visuals", False),
                "include_question": not analysis.get("has_question", False),
                "use_emojis": True,
                "short_paragraphs": True,
                "call_to_action": "Like, Comment, Share"
            },
            "engagement_tactics": [
                "Reply to all comments within 2 hours",
                "Tag friends who might be interested",
                "Create shareable moments",
                "Use polls to increase engagement",
                "Post videos for higher reach"
            ]
        }

    def _recommend_instagram(self, analysis: Dict, tone: Dict) -> Dict[str, Any]:
        """Instagram-specific recommendations"""
        return {
            "platform": "Instagram",
            "primary_strategy": "Visual storytelling",
            "character_limit": 2200,
            "posting_frequency": "1-2 times daily (Stories and Posts)",
            "optimal_posting_times": ["11 AM", "7-9 PM"],
            "content_guidelines": [
                "50-150 words for captions",
                f"Your content: {analysis.get('word_count', 0)} words - {'Shorten for Instagram' if analysis.get('word_count', 0) > 150 else 'Good length'}",
                "High-quality image is ESSENTIAL",
                f"Visuals: {'Perfect!' if analysis.get('has_visuals') else 'Image is required'}",
                "Use 10-30 hashtags"
            ],
            "best_practices": [
                "Tell a story through captions",
                "Use emojis strategically",
                "Create call-to-action",
                "Post Stories for daily engagement",
                "Use Reels for maximum reach"
            ],
            "formatting_suggestions": {
                "high_quality_image": True,
                "hashtags_count": 15,
                "use_emojis": True,
                "add_story": True,
                "video_reels": True,
                "call_to_action": "Link in bio or Save this post"
            },
            "engagement_tactics": [
                "Engage with hashtags related to your niche",
                "Reply to all DMs and comments",
                "Follow and engage with similar accounts",
                "Use Stories to build anticipation",
                "Go Live weekly for real-time connection"
            ]
        }

    def _recommend_tiktok(self, analysis: Dict, tone: Dict) -> Dict[str, Any]:
        """TikTok-specific recommendations"""
        return {
            "platform": "TikTok",
            "primary_strategy": "Authentic, entertaining short-form video",
            "character_limit": 2500,
            "posting_frequency": "1-3 times daily",
            "optimal_posting_times": ["Consistency matters more than time"],
            "content_guidelines": [
                "15 seconds to 10 minutes ideal",
                "Vertical video format (9:16)",
                f"Has visuals: {'Use video' if analysis.get('has_visuals') else 'Record short video'}",
                "Hook viewer in first 3 seconds"
            ],
            "best_practices": [
                "Be authentic and casual",
                "Use trending sounds and hashtags",
                "Show personality",
                "Include text overlays",
                "End with call-to-action or question"
            ],
            "formatting_suggestions": {
                "video_format": "Vertical (9:16)",
                "duration": "15-60 seconds",
                "trending_sounds": True,
                "text_overlays": True,
                "call_to_action": True,
                "hashtags": 5
            },
            "engagement_tactics": [
                "Post consistently (algorithm rewards regularity)",
                "Engage with your niche's trending content",
                "Respond to all comments",
                "Create duets and stitches",
                "Go Live and connect with community"
            ]
        }

    def _recommend_email(self, analysis: Dict, tone: Dict) -> Dict[str, Any]:
        """Email-specific recommendations"""
        return {
            "platform": "Email",
            "primary_strategy": "Direct, personalized communication",
            "character_limit": "Unlimited",
            "send_frequency": "1-2 times weekly",
            "optimal_send_times": ["9 AM", "5 PM"],
            "content_guidelines": [
                "Subject line: 30-50 characters",
                f"Your content: {analysis.get('word_count', 0)} words - {'Could expand' if analysis.get('word_count', 0) < 50 else 'Good for email'}",
                "Short paragraphs (2-3 sentences max)",
                "One clear call-to-action"
            ],
            "best_practices": [
                "Personalize with recipient name",
                "Lead with benefits, not features",
                f"Include CTA: {'Yes' if analysis.get('has_cta') else 'Add call-to-action'}",
                "Make it scannable with headers",
                "Mobile-first design"
            ],
            "formatting_suggestions": {
                "personalization": "{{first_name}}",
                "subject_line": "Action-oriented",
                "preview_text": "40-50 chars",
                "headers": True,
                "bold_key_points": True,
                "button_cta": True,
                "mobile_responsive": True
            },
            "engagement_tactics": [
                "A/B test subject lines",
                "Segment email list by behavior",
                "Include clear unsubscribe link",
                "Track opens and clicks",
                "Follow up based on engagement"
            ]
        }

    def _recommend_blog(self, analysis: Dict, tone: Dict) -> Dict[str, Any]:
        """Blog-specific recommendations"""
        return {
            "platform": "Blog",
            "primary_strategy": "Long-form SEO and thought leadership",
            "character_limit": "Unlimited",
            "posting_frequency": "1-2 times weekly",
            "optimal_posting_times": ["Tuesday-Thursday 10 AM"],
            "content_guidelines": [
                f"Target length: 1,000-2,500 words",
                f"Your content: {analysis.get('word_count', 0)} words - {'Expand significantly' if analysis.get('word_count', 0) < 500 else 'Good length'}",
                "Include headers (H2, H3) for structure",
                "Add relevant images throughout"
            ],
            "best_practices": [
                "Start with compelling introduction",
                "Use clear subheadings",
                "Include relevant internal links",
                f"Formality: {tone.get('formality')} is appropriate",
                "End with clear conclusion and CTA"
            ],
            "formatting_suggestions": {
                "headers": True,
                "images": 3,
                "internal_links": 5,
                "external_links": 3,
                "bullet_points": True,
                "code_snippets": False,
                "meta_description": "150-160 chars"
            },
            "engagement_tactics": [
                "Optimize title for SEO",
                "Include related posts section",
                "Add social sharing buttons",
                "Encourage comments",
                "Update old posts with new info"
            ]
        }

    def _recommend_generic(self, platform: str, analysis: Dict, tone: Dict) -> Dict[str, Any]:
        """Generic recommendations for unknown platform"""
        return {
            "platform": platform,
            "primary_strategy": "Adapt content to platform norms",
            "character_limit": "Varies",
            "posting_frequency": "1-2 times daily",
            "content_guidelines": [
                f"Your content: {analysis.get('word_count', 0)} words",
                "Research platform-specific best practices",
                "Follow community guidelines"
            ],
            "best_practices": [
                f"Tone: {tone.get('tone')}",
                f"Sentiment: {tone.get('sentiment')}",
                "Engage with community",
                "Test different approaches"
            ]
        }


class ContentOptimizationTool:
    """Generate platform-specific optimized versions of content"""

    def __init__(self):
        self.name = "content_optimization"
        self.description = "Generate optimized versions of content for each platform"

    async def _execute(
        self,
        original_content: str,
        platform: str,
        tone_preference: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate optimized content for platform"""

        logger.info(f"Optimizing content for {platform}")

        try:
            optimized = self._optimize_for_platform(original_content, platform, tone_preference)

            return {
                "success": True,
                "platform": platform,
                "original_length": len(original_content.split()),
                "optimized_content": optimized["content"],
                "optimized_length": len(optimized["content"].split()),
                "changes_made": optimized["changes"],
                "hashtags": optimized.get("hashtags", []),
                "character_count": len(optimized["content"]),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _optimize_for_platform(self, content: str, platform: str, tone: str = None) -> Dict[str, Any]:
        """Optimize content for specific platform"""

        if platform.lower() == "twitter":
            return self._optimize_twitter(content)
        elif platform.lower() == "linkedin":
            return self._optimize_linkedin(content)
        elif platform.lower() == "facebook":
            return self._optimize_facebook(content)
        elif platform.lower() == "instagram":
            return self._optimize_instagram(content)
        elif platform.lower() == "tiktok":
            return self._optimize_tiktok(content)
        elif platform.lower() == "email":
            return self._optimize_email(content)
        elif platform.lower() == "blog":
            return self._optimize_blog(content)
        else:
            return {"content": content, "changes": []}

    def _optimize_twitter(self, content: str) -> Dict[str, Any]:
        """Optimize for Twitter (280 char limit)"""
        changes = []
        optimized = content

        # Truncate if needed
        if len(optimized) > 250:
            optimized = optimized[:250].rsplit(' ', 1)[0] + "..."
            changes.append("Truncated to fit 280 character limit")

        # Add emojis if none exist
        if "😊" not in optimized and "🎉" not in optimized:
            optimized += " 🎯"
            changes.append("Added emoji for engagement")

        # Ensure hashtags
        if "#" not in optimized:
            optimized += " #trending"
            changes.append("Added relevant hashtag")

        return {
            "content": optimized,
            "changes": changes,
            "hashtags": self._extract_hashtags(optimized)
        }

    def _optimize_linkedin(self, content: str) -> Dict[str, Any]:
        """Optimize for LinkedIn"""
        changes = []
        optimized = content

        # Add line breaks for readability
        sentences = optimized.split('. ')
        if len(sentences) > 3:
            optimized = '.\n\n'.join(sentences)
            changes.append("Added line breaks for readability")

        # Capitalize first letters of key points
        optimized = optimized.replace("- ", "• ")
        changes.append("Formatted bullet points")

        # Add professional closing
        if not optimized.endswith("?") and not optimized.endswith("!"):
            optimized += "\n\nWhat are your thoughts?"
            changes.append("Added engagement question")

        return {
            "content": optimized,
            "changes": changes,
            "hashtags": self._extract_hashtags(optimized)
        }

    def _optimize_facebook(self, content: str) -> Dict[str, Any]:
        """Optimize for Facebook"""
        changes = []
        optimized = content

        # Add emojis
        if "😊" not in optimized:
            optimized = "👉 " + optimized
            changes.append("Added emoji for visibility")

        # Add engagement hook
        if "?" not in optimized:
            optimized += "\n\nWhat do you think? 👇"
            changes.append("Added engagement hook")

        return {
            "content": optimized,
            "changes": changes,
            "hashtags": []
        }

    def _optimize_instagram(self, content: str) -> Dict[str, Any]:
        """Optimize for Instagram"""
        changes = []
        optimized = content

        # Shorten if too long
        if len(optimized) > 150:
            optimized = optimized[:150]
            changes.append("Shortened for Instagram caption")

        # Add relevant hashtags (max 30)
        hashtags = self._generate_instagram_hashtags(optimized)
        optimized += "\n\n" + " ".join([f"#{tag}" for tag in hashtags[:20]])
        changes.append(f"Added {len(hashtags)} hashtags")

        # Add emojis
        optimized = "✨ " + optimized
        changes.append("Added opening emoji")

        return {
            "content": optimized,
            "changes": changes,
            "hashtags": hashtags
        }

    def _optimize_tiktok(self, content: str) -> Dict[str, Any]:
        """Optimize for TikTok"""
        changes = []
        optimized = content

        # Make casual
        optimized = optimized.lower()
        changes.append("Converted to casual tone")

        # Add hook
        optimized = "POV: " + optimized
        changes.append("Added hook for video")

        # Add hashtags
        if "#" not in optimized:
            optimized += " #foryoupage #viral"
            changes.append("Added trending hashtags")

        return {
            "content": optimized,
            "changes": changes,
            "hashtags": self._extract_hashtags(optimized)
        }

    def _optimize_email(self, content: str) -> Dict[str, Any]:
        """Optimize for Email"""
        changes = []
        optimized = content

        # Ensure CTA
        if "click" not in optimized.lower() and "visit" not in optimized.lower():
            optimized += "\n\n[Click here to learn more](https://example.com)"
            changes.append("Added call-to-action")

        # Add professional greeting
        optimized = "Hi {{first_name}},\n\n" + optimized
        changes.append("Added personalization")

        # Add signature
        optimized += "\n\nBest regards,\nThe Team"
        changes.append("Added professional signature")

        return {
            "content": optimized,
            "changes": changes,
            "hashtags": []
        }

    def _optimize_blog(self, content: str) -> Dict[str, Any]:
        """Optimize for Blog"""
        changes = []
        optimized = content

        # Ensure structure
        if "<h2>" not in optimized:
            optimized = "## Introduction\n\n" + optimized
            changes.append("Added markdown headers")

        # Add conclusion
        if not optimized.endswith("?") and not optimized.endswith("."):
            optimized += "\n\n## Conclusion\n\nThese insights should help guide your strategy."
            changes.append("Added conclusion section")

        return {
            "content": optimized,
            "changes": changes,
            "hashtags": []
        }

    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        import re
        return re.findall(r'#\w+', content)

    def _generate_instagram_hashtags(self, content: str) -> List[str]:
        """Generate relevant Instagram hashtags"""
        keywords = content.lower().split()
        hashtags = ["insta", "daily", "instagood"]
        hashtags.extend(keywords[:5])
        return hashtags


# Singleton instances
platform_recommendation = PlatformRecommendationTool()
content_optimization = ContentOptimizationTool()
