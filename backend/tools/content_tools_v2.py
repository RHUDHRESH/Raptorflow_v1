"""
CONTENT TOOLS v2 - Content strategy and generation
Calendar generation, platform optimization, narrative building, multi-channel adaptation
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ContentCalendarGeneratorTool(BaseTool):
    """Generate content calendar aligned with positioning"""

    def __init__(self):
        super().__init__(
            name="content_calendar_generator",
            description="Generate 90-day content calendar aligned with positioning and RACE strategy"
        )

    async def _execute(
        self,
        positioning: Dict,
        icps: List[Dict],
        channels: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate content calendar"""
        logger.info("Generating content calendar")

        try:
            channels = channels or ["blog", "social", "email", "video"]
            calendar = {}

            # Generate 90 days of content (approximately 13 weeks)
            base_date = datetime.now()

            for week in range(1, 14):
                week_start = base_date + timedelta(weeks=week-1)
                week_key = f"Week {week}"

                calendar[week_key] = {
                    "start_date": week_start.strftime("%Y-%m-%d"),
                    "theme": self._generate_weekly_theme(week, positioning),
                    "content_pieces": self._generate_content_pieces(week, positioning, icps, channels),
                    "distribution_plan": self._plan_distribution(channels),
                    "metrics": {
                        "target_reach": 5000 * week,
                        "target_engagement": 250 * week,
                        "conversion_target": 10 + (week * 2)
                    }
                }

            return {
                "success": True,
                "period": "90 days (13 weeks)",
                "start_date": base_date.strftime("%Y-%m-%d"),
                "positioning_word": positioning.get("word"),
                "channels": channels,
                "content_calendar": calendar,
                "summary": {
                    "total_pieces": 13 * len(channels),
                    "estimated_hours": 13 * len(channels) * 2,
                    "primary_focus": positioning.get("big_idea")
                }
            }

        except Exception as e:
            logger.error(f"Content calendar generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_weekly_theme(self, week: int, positioning: Dict) -> str:
        """Generate weekly content theme"""
        themes = [
            "Introduce the problem",
            "Deep dive into pain points",
            "Showcase market trends",
            "Competitor landscape",
            "Your unique approach",
            "Customer benefits",
            "Feature spotlight",
            "Case study highlight",
            "Expert insights",
            "Industry analysis",
            "Best practices guide",
            "Implementation tips",
            "Success celebration"
        ]
        return themes[week - 1] if week <= len(themes) else themes[-1]

    def _generate_content_pieces(
        self,
        week: int,
        positioning: Dict,
        icps: List[Dict],
        channels: List[str]
    ) -> List[Dict]:
        """Generate content pieces for week"""
        pieces = []

        for channel in channels:
            piece = {
                "channel": channel,
                "type": self._determine_content_type(channel),
                "title": self._generate_title(week, positioning),
                "description": self._generate_description(positioning),
                "target_audience": self._select_target_icp(icps),
                "cta": f"Learn more about {positioning.get('word', 'our offering')}",
                "estimated_duration": self._estimate_duration(channel)
            }
            pieces.append(piece)

        return pieces

    def _determine_content_type(self, channel: str) -> str:
        """Determine content type by channel"""
        types = {
            "blog": "Long-form article",
            "social": "Social media post",
            "email": "Email campaign",
            "video": "Video content",
            "podcast": "Audio episode"
        }
        return types.get(channel, "Content piece")

    def _generate_title(self, week: int, positioning: Dict) -> str:
        """Generate content title"""
        word = positioning.get("word", "Business")
        return f"Week {week}: How {word} Transforms Your {positioning.get('category', 'Business')}"

    def _generate_description(self, positioning: Dict) -> str:
        """Generate content description"""
        return f"Explore how {positioning.get('word')} positioning helps achieve {positioning.get('customer_promise', 'business goals')}"

    def _select_target_icp(self, icps: List[Dict]) -> str:
        """Select target ICP for content"""
        if icps:
            return icps[0].get("name", "All segments")
        return "All segments"

    def _estimate_duration(self, channel: str) -> str:
        """Estimate content creation duration"""
        durations = {
            "blog": "4-6 hours",
            "social": "1-2 hours",
            "email": "2-3 hours",
            "video": "8-12 hours",
            "podcast": "6-8 hours"
        }
        return durations.get(channel, "3-4 hours")

    def _plan_distribution(self, channels: List[str]) -> Dict:
        """Plan content distribution"""
        return {
            "frequency": "3x per week",
            "best_times": {
                "blog": "Tuesday, 9am",
                "social": "Monday, 9am / Wednesday, 5pm / Friday, 2pm",
                "email": "Tuesday, 10am",
                "video": "Thursday, 3pm"
            },
            "repurposing": "Transform blog into social posts, video clips, and email content"
        }


class PlatformOptimizationTool(BaseTool):
    """Optimize content for specific platforms"""

    def __init__(self):
        super().__init__(
            name="platform_optimizer",
            description="Optimize content strategy for each platform based on ICP behavior"
        )

    async def _execute(
        self,
        positioning: Dict,
        icps: List[Dict],
        available_platforms: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Optimize platform strategy"""
        logger.info("Optimizing platform strategy")

        try:
            # Extract platforms from ICPs
            platform_set = set()
            for icp in icps:
                platforms = icp.get("behavior", {}).get("top_platforms", [])
                platform_set.update(platforms)

            platforms = available_platforms or list(platform_set) or [
                "LinkedIn", "Twitter", "Instagram", "TikTok", "YouTube", "Email"
            ]

            platform_strategies = {}

            for platform in platforms:
                strategy = self._generate_platform_strategy(platform, positioning, icps)
                platform_strategies[platform] = strategy

            # Calculate platform priority
            priorities = self._rank_platform_priority(platform_strategies, icps)

            return {
                "success": True,
                "platforms_analyzed": len(platforms),
                "platform_strategies": platform_strategies,
                "platform_priority": priorities,
                "recommendation": f"Focus on {priorities[0]['platform']} for highest ROI"
            }

        except Exception as e:
            logger.error(f"Platform optimization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_platform_strategy(self, platform: str, positioning: Dict, icps: List[Dict]) -> Dict:
        """Generate strategy for specific platform"""
        return {
            "platform": platform,
            "primary_format": self._get_primary_format(platform),
            "posting_frequency": self._get_posting_frequency(platform),
            "content_themes": self._get_content_themes(platform, positioning),
            "hashtags": self._generate_hashtags(positioning, platform),
            "best_times": self._get_best_times(platform),
            "kpis": self._get_platform_kpis(platform),
            "content_tips": self._get_platform_tips(platform)
        }

    def _get_primary_format(self, platform: str) -> str:
        """Get primary content format for platform"""
        formats = {
            "LinkedIn": "Professional articles and thought leadership",
            "Twitter": "Bite-sized insights and engaging threads",
            "Instagram": "Visual storytelling with carousel posts",
            "TikTok": "Short-form video trends and entertainment",
            "YouTube": "Long-form educational video content",
            "Email": "Personalized messages and newsletters"
        }
        return formats.get(platform, "Multimedia content")

    def _get_posting_frequency(self, platform: str) -> str:
        """Get recommended posting frequency"""
        frequencies = {
            "LinkedIn": "3-5x per week",
            "Twitter": "1-3x per day",
            "Instagram": "1-2x per day",
            "TikTok": "1-3x per day",
            "YouTube": "1-2x per week",
            "Email": "1-2x per week"
        }
        return frequencies.get(platform, "2-3x per week")

    def _get_content_themes(self, platform: str, positioning: Dict) -> List[str]:
        """Get content themes for platform"""
        word = positioning.get("word", "Business")
        return [
            f"Why {word} matters",
            "Industry trends and insights",
            "Success stories and case studies",
            "Practical tips and guides",
            "Behind-the-scenes content",
            f"How to leverage {word}"
        ]

    def _generate_hashtags(self, positioning: Dict, platform: str) -> List[str]:
        """Generate platform-specific hashtags"""
        word = positioning.get("word", "")
        base_hashtags = [f"#{word}", "#BusinessStrategy", "#Growth"]

        platform_specific = {
            "LinkedIn": ["#ThoughtLeadership", "#BusinessInnovation"],
            "Twitter": ["#MarketingStrategy", "#BusinessTips"],
            "Instagram": ["#BusinessLife", "#Entrepreneurship"],
            "TikTok": ["#BusinessTok", "#EntrepreneurLife"]
        }

        return base_hashtags + platform_specific.get(platform, [])

    def _get_best_times(self, platform: str) -> str:
        """Get best posting times"""
        times = {
            "LinkedIn": "Tuesday-Thursday, 8-10am or 5-6pm",
            "Twitter": "Wednesday, 9am EST",
            "Instagram": "Tuesday-Friday, 11am or 7pm",
            "TikTok": "6-10pm (evening peak)",
            "YouTube": "Thursday, 3pm EST",
            "Email": "Tuesday or Thursday, 10am"
        }
        return times.get(platform, "9am-2pm")

    def _get_platform_kpis(self, platform: str) -> List[str]:
        """Get platform-specific KPIs"""
        kpis = {
            "LinkedIn": ["Engagement rate", "Click-through rate", "Profile views"],
            "Twitter": ["Retweets", "Replies", "Click-throughs"],
            "Instagram": ["Likes", "Saves", "Story interactions"],
            "TikTok": ["Views", "Completion rate", "Shares"],
            "YouTube": ["Watch time", "Retention rate", "Subscribers"],
            "Email": ["Open rate", "Click rate", "Conversions"]
        }
        return kpis.get(platform, ["Reach", "Engagement", "Conversions"])

    def _get_platform_tips(self, platform: str) -> List[str]:
        """Get platform-specific tips"""
        tips = {
            "LinkedIn": ["Use professional tone", "Provide value first", "Engage authentically"],
            "Twitter": ["Be concise and witty", "Use threads for depth", "Join conversations"],
            "Instagram": ["Focus on visuals", "Tell stories", "Use captions effectively"],
            "TikTok": ["Embrace trends", "Keep it authentic", "Short and snappy"],
            "YouTube": ["Optimize titles and descriptions", "Create compelling thumbnails", "Consistent uploads"],
            "Email": ["Personalize content", "Clear call-to-action", "Mobile optimization"]
        }
        return tips.get(platform, ["Be authentic", "Add value", "Engage audience"])

    def _rank_platform_priority(self, strategies: Dict, icps: List[Dict]) -> List[Dict]:
        """Rank platforms by priority"""
        priorities = []

        for platform, strategy in strategies.items():
            # Calculate priority based on platform and ICP alignment
            priority_score = self._calculate_platform_priority(platform, icps)
            priorities.append({
                "platform": platform,
                "priority_score": priority_score,
                "recommendation": "High priority" if priority_score > 0.7 else "Medium priority" if priority_score > 0.4 else "Low priority"
            })

        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        return priorities


class NarrativeBuilderTool(BaseTool):
    """Build brand narrative and messaging framework"""

    def __init__(self):
        super().__init__(
            name="narrative_builder",
            description="Build cohesive brand narrative and messaging framework"
        )

    async def _execute(
        self,
        positioning: Dict,
        business_data: Dict,
        icps: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Build brand narrative"""
        logger.info("Building brand narrative")

        try:
            # Create narrative arc
            narrative_arc = {
                "situation": self._build_situation_narrative(business_data),
                "conflict": self._build_conflict_narrative(positioning),
                "resolution": self._build_resolution_narrative(positioning),
                "transformation": self._build_transformation_narrative(positioning, icps)
            }

            # Create messaging framework
            messaging_framework = {
                "headline": self._create_headline(positioning),
                "subheadline": self._create_subheadline(positioning),
                "core_message": positioning.get("customer_promise", ""),
                "supporting_messages": self._create_supporting_messages(positioning),
                "key_benefits": self._extract_benefits(positioning),
                "objection_handlers": self._create_objection_handlers(positioning)
            }

            # Create story formats
            story_formats = {
                "elevator_pitch": self._create_elevator_pitch(positioning),
                "case_study_template": self._create_case_study_template(),
                "customer_testimonial_guide": self._create_testimonial_guide(),
                "brand_story": self._create_brand_story(positioning, business_data)
            }

            return {
                "success": True,
                "brand_positioning": positioning.get("word"),
                "narrative_arc": narrative_arc,
                "messaging_framework": messaging_framework,
                "story_formats": story_formats,
                "recommendation": "Use consistent narrative across all channels"
            }

        except Exception as e:
            logger.error(f"Narrative building failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_situation_narrative(self, business_data: Dict) -> str:
        """Build situation part of narrative"""
        return f"In the {business_data.get('industry', 'industry')}, {business_data.get('name', 'companies')} face unique challenges."

    def _build_conflict_narrative(self, positioning: Dict) -> str:
        """Build conflict in narrative"""
        return f"The market lacks clear {positioning.get('word', 'positioning')} in this space."

    def _build_resolution_narrative(self, positioning: Dict) -> str:
        """Build resolution narrative"""
        return f"{positioning.get('word', 'Our approach')} provides the solution."

    def _build_transformation_narrative(self, positioning: Dict, icps: List[Dict]) -> str:
        """Build transformation narrative"""
        if icps:
            icp_name = icps[0].get("name", "customers")
            return f"{icp_name} can now {positioning.get('customer_promise', 'achieve their goals')}"
        return f"You can now {positioning.get('customer_promise', 'succeed')}"

    def _create_headline(self, positioning: Dict) -> str:
        """Create main headline"""
        return f"Discover {positioning.get('word', 'the power')} of {positioning.get('category', 'transformation')}"

    def _create_subheadline(self, positioning: Dict) -> str:
        """Create subheadline"""
        return positioning.get("big_idea", "Transform your business")

    def _create_supporting_messages(self, positioning: Dict) -> List[str]:
        """Create supporting messages"""
        differentiators = positioning.get("differentiation", "").split(".")
        return [d.strip() for d in differentiators if d.strip()][:3]

    def _extract_benefits(self, positioning: Dict) -> List[str]:
        """Extract key benefits"""
        return [
            f"Achieve: {positioning.get('customer_promise', 'your goals')}",
            f"Benefit from: {positioning.get('word', 'unique positioning')}",
            f"Experience: {positioning.get('purple_cow', 'remarkable results')}"
        ]

    def _create_objection_handlers(self, positioning: Dict) -> Dict:
        """Create objection handling responses"""
        return {
            "cost": "The investment pays for itself through improved results.",
            "complexity": f"{positioning.get('word', 'Our approach')} is designed for simplicity.",
            "risk": "We provide guarantees and support every step of the way."
        }

    def _create_elevator_pitch(self, positioning: Dict) -> str:
        """Create 30-second elevator pitch"""
        return f"We help {positioning.get('category', 'companies')} achieve {positioning.get('customer_promise', 'success')} through {positioning.get('word', 'innovative positioning')}."

    def _create_case_study_template(self) -> Dict:
        """Create case study template"""
        return {
            "client_name": "Example Client",
            "challenge": "Description of client's challenge",
            "solution": "How we solved it",
            "results": {
                "metric_1": "X% improvement",
                "metric_2": "Y increase",
                "metric_3": "Z growth"
            },
            "quote": "Client testimonial about experience",
            "call_to_action": "Learn how we can help you achieve similar results"
        }

    def _create_testimonial_guide(self) -> Dict:
        """Create customer testimonial guide"""
        return {
            "structure": ["Challenge", "Solution", "Results", "Recommendation"],
            "length": "50-100 words",
            "tone": "Authentic and specific",
            "tips": [
                "Focus on measurable results",
                "Use specific metrics",
                "Show personality",
                "Address common objections"
            ]
        }

    def _create_brand_story(self, positioning: Dict, business_data: Dict) -> str:
        """Create brand story"""
        return f"{business_data.get('name', 'Our company')} was founded with a belief: {positioning.get('big_idea', 'to transform the industry')}. Today, we help {positioning.get('category', 'our customers')} achieve {positioning.get('customer_promise', 'their goals')} through {positioning.get('word', 'innovative approaches')}."


# Singleton instances
content_calendar_generator = ContentCalendarGeneratorTool()
platform_optimizer = PlatformOptimizationTool()
narrative_builder = NarrativeBuilderTool()
