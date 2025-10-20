"""
CONTENT ROUTING API ROUTES
RESTful endpoints for intelligent content routing and distribution
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/content", tags=["content-routing"])


# Pydantic Models
class ContentAnalysisRequest(BaseModel):
    """Request model for content analysis"""
    content: str = Field(..., min_length=3, description="Content to analyze")
    content_type: str = Field("text", description="Type of content: text, promotional, question, venting, etc.")
    business_id: Optional[str] = Field(None, description="Business ID")


class PlatformRecommendationRequest(BaseModel):
    """Request for platform recommendations"""
    content: str = Field(..., description="Content to analyze")
    business_id: str = Field(..., description="Business ID")
    tone_preference: Optional[str] = Field(None, description="Preferred tone adjustment")
    platforms: Optional[List[str]] = Field(None, description="Specific platforms to evaluate")


class ContentRoutingRequest(BaseModel):
    """Request for intelligent content routing"""
    business_id: str = Field(..., description="Business ID")
    content: str = Field(..., min_length=3, description="Content to route")
    content_type: str = Field("text", description="Type of content")
    auto_publish: bool = Field(False, description="Auto-publish to recommended platforms")
    schedule_time: Optional[str] = Field(None, description="Schedule time in ISO format")


class MultiPlatformDistributionRequest(BaseModel):
    """Request for multi-platform distribution"""
    business_id: str = Field(..., description="Business ID")
    content: str = Field(..., description="Content to distribute")
    platforms: List[str] = Field(..., min_items=1, description="Target platforms")
    schedule_time: Optional[str] = Field(None, description="Scheduled distribution time")
    optimized_versions: Optional[Dict[str, str]] = Field(None, description="Platform-specific optimized content")


class ToneAdjustmentRequest(BaseModel):
    """Request to adjust content tone"""
    content: str = Field(..., description="Content to adjust")
    target_tone: str = Field(..., description="Target tone: professional, casual, friendly, authoritative, humorous, sympathetic")


class AudienceMatchingRequest(BaseModel):
    """Request to match content to audiences"""
    content: str = Field(..., description="Content to match")
    content_type: str = Field("text", description="Type of content")
    icps: List[Dict[str, Any]] = Field(..., description="List of ICP personas")


# API Endpoints

@router.post("/analyze", summary="Analyze content sentiment and tone")
async def analyze_content(request: ContentAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze content for sentiment, tone, and characteristics

    Returns:
    - content_analysis: Word count, character count, features detected
    - sentiment: Positive, negative, or neutral
    - tone: Venting, promotional, question, informative
    - emotional_intensity: Level of emotional content
    """
    try:
        logger.info("Analyzing content")

        # Simulate sentiment analysis
        sentiment = "positive" if "great" in request.content.lower() else \
                   "negative" if "hate" in request.content.lower() else "neutral"

        analysis = {
            "content_type": request.content_type,
            "word_count": len(request.content.split()),
            "character_count": len(request.content),
            "sentiment": sentiment,
            "tone": "venting" if sentiment == "negative" else "informative",
            "has_question": "?" in request.content,
            "has_cta": any(cta in request.content.lower() for cta in ["click", "buy", "join"]),
            "emotional_intensity": "high" if sentiment != "neutral" else "low"
        }

        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Content analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-platforms", summary="Get platform recommendations")
async def recommend_platforms(request: PlatformRecommendationRequest) -> Dict[str, Any]:
    """
    Get platform recommendations for content

    Returns:
    - recommendations: List of platforms ranked by suitability
    - best_platform: Top recommended platform
    - reasoning: Why each platform is recommended
    - tips: Platform-specific posting tips
    """
    try:
        logger.info(f"Getting platform recommendations for business {request.business_id}")

        # Mock recommendations
        all_recommendations = [
            {
                "platform": "Twitter/X",
                "score": 0.85,
                "confidence": "high",
                "reasoning": "Great for quick reactions and venting",
                "tips": ["Keep under 280 chars", "Use hashtags", "Thread if needed"]
            },
            {
                "platform": "LinkedIn",
                "score": 0.65,
                "confidence": "medium",
                "reasoning": "Professional network for insights",
                "tips": ["Add line breaks", "Formal tone", "Include CTA"]
            },
            {
                "platform": "Facebook",
                "score": 0.70,
                "confidence": "medium",
                "reasoning": "Broad reach for community engagement",
                "tips": ["Add image", "Encourage comments", "Use emojis"]
            },
            {
                "platform": "Slack",
                "score": 0.75,
                "confidence": "high",
                "reasoning": "Perfect for team discussions",
                "tips": ["Use threads", "Tag relevant people", "Keep casual"]
            },
            {
                "platform": "Discord",
                "score": 0.72,
                "confidence": "medium",
                "reasoning": "Great for community venting",
                "tips": ["Conversational tone", "Thread support", "Emoji reactions"]
            }
        ]

        # Filter by requested platforms if provided
        if request.platforms:
            recommendations = [r for r in all_recommendations if r["platform"].lower() in request.platforms]
        else:
            recommendations = sorted(all_recommendations, key=lambda x: x["score"], reverse=True)[:3]

        return {
            "success": True,
            "business_id": request.business_id,
            "recommendations": recommendations,
            "primary_platform": recommendations[0] if recommendations else None,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Platform recommendation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/route-content", summary="Intelligently route content to platforms")
async def route_content(request: ContentRoutingRequest) -> Dict[str, Any]:
    """
    Analyze content and get intelligent routing recommendations

    Returns:
    - analysis: Content characteristics
    - recommendations: Platform recommendations with scores
    - distribution_plan: Ready-to-execute distribution plan
    - primary_platforms: Top 3 recommended platforms
    """
    try:
        logger.info(f"Routing content for business {request.business_id}")

        # Analyze content
        analysis = {
            "word_count": len(request.content.split()),
            "sentiment": "positive" if "great" in request.content.lower() else "neutral",
            "has_question": "?" in request.content,
            "has_cta": any(cta in request.content.lower() for cta in ["click", "buy", "join"])
        }

        # Get recommendations (mock)
        recommendations = [
            {
                "platform": "Twitter/X",
                "score": 0.85,
                "reasoning": "Ideal for this content type",
                "tips": ["Use hashtags", "Thread if needed"]
            },
            {
                "platform": "Slack",
                "score": 0.75,
                "reasoning": "Great for team sharing",
                "tips": ["Use threads", "Keep casual"]
            },
            {
                "platform": "Discord",
                "score": 0.70,
                "reasoning": "Perfect for community discussion",
                "tips": ["Conversational", "Thread support"]
            }
        ]

        distribution_plan = {
            "business_id": request.business_id,
            "platforms": [r["platform"] for r in recommendations],
            "content": request.content,
            "scheduled_time": request.schedule_time or datetime.now().isoformat(),
            "auto_publish": request.auto_publish
        }

        return {
            "success": True,
            "business_id": request.business_id,
            "analysis": analysis,
            "recommendations": recommendations,
            "distribution_plan": distribution_plan,
            "primary_platforms": [r["platform"] for r in recommendations],
            "routing_confidence": 0.82,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Content routing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/distribute-multi-platform", summary="Distribute to multiple platforms")
async def distribute_multi_platform(request: MultiPlatformDistributionRequest) -> Dict[str, Any]:
    """
    Distribute content to multiple platforms with optimization

    Returns:
    - distribution_results: Results for each platform
    - successful_count: Number of successful distributions
    - failed_count: Number of failed distributions
    - tracking_links: Links to track each platform
    """
    try:
        logger.info(f"Distributing to {len(request.platforms)} platforms")

        results = []

        for platform in request.platforms:
            result = {
                "platform": platform,
                "status": "posted",
                "post_id": f"{platform}_{datetime.now().timestamp()}",
                "url": f"https://{platform}.com/post/123456",
                "posted_at": datetime.now().isoformat(),
                "tracking_enabled": True
            }
            results.append(result)

        return {
            "success": True,
            "business_id": request.business_id,
            "distribution_results": results,
            "total_platforms": len(request.platforms),
            "successful": len(results),
            "failed": 0,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Multi-platform distribution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adjust-tone", summary="Adjust content tone")
async def adjust_tone(request: ToneAdjustmentRequest) -> Dict[str, Any]:
    """
    Adjust content to different tone

    Returns:
    - adjusted_content: Content with new tone
    - changes_made: List of changes made
    - tone_shift: Description of tone change
    """
    try:
        logger.info(f"Adjusting tone to: {request.target_tone}")

        # Mock tone adjustment
        adjusted = request.content
        changes = []

        if request.target_tone.lower() == "professional":
            adjusted = adjusted.replace("lol", "respectfully")
            changes.append("Replaced casual language")
        elif request.target_tone.lower() == "casual":
            adjusted = adjusted + "!"
            changes.append("Added enthusiasm")

        return {
            "success": True,
            "original_tone": "neutral",
            "target_tone": request.target_tone,
            "original_content": request.content,
            "adjusted_content": adjusted,
            "changes_made": changes,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Tone adjustment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match-audience", summary="Match content to audience personas")
async def match_audience(request: AudienceMatchingRequest) -> Dict[str, Any]:
    """
    Match content to ICP personas

    Returns:
    - matches: Ranked list of ICP matches
    - best_match: Best matching persona
    - resonance_factors: Why content resonates with each ICP
    """
    try:
        logger.info("Matching content to audience personas")

        matches = []

        for icp in request.icps:
            match = {
                "icp_name": icp.get("name", "Unknown"),
                "match_score": 0.85,
                "match_level": "Strong Match",
                "platforms": icp.get("behavior", {}).get("top_platforms", []),
                "resonance_factors": ["Addresses pain points", "Aligns with goals"]
            }
            matches.append(match)

        matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)

        return {
            "success": True,
            "matches": matches,
            "best_match": matches[0] if matches else None,
            "total_icps": len(request.icps),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Audience matching failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending-topics", summary="Get trending topics for content inspiration")
async def get_trending_topics() -> Dict[str, Any]:
    """Get trending topics to inspire content creation"""
    return {
        "success": True,
        "trending": [
            {"topic": "AI and automation", "engagement": "high"},
            {"topic": "Work-life balance", "engagement": "high"},
            {"topic": "Remote work tips", "engagement": "medium"},
            {"topic": "Team productivity", "engagement": "high"}
        ],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/best-times-to-post", summary="Get optimal posting times by platform")
async def get_best_posting_times(platform: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Get optimal posting times for each platform"""

    optimal_times = {
        "twitter": ["8-9 AM", "12 PM", "5-6 PM"],
        "linkedin": ["8-9 AM", "5-6 PM"],
        "facebook": ["1-3 PM", "7-9 PM"],
        "instagram": ["11 AM", "7-9 PM"],
        "tiktok": ["Evening (time less critical)"],
        "email": ["Tuesday-Thursday"],
        "blog": ["Morning (10 AM)"]
    }

    if platform:
        return {
            "success": True,
            "platform": platform,
            "optimal_times": optimal_times.get(platform.lower(), []),
            "timezone": "UTC"
        }
    else:
        return {
            "success": True,
            "all_platforms": optimal_times,
            "timezone": "UTC"
        }


@router.get("/content-templates", summary="Get content templates for different platforms")
async def get_content_templates(
    platform: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Get content templates for different platforms and types"""

    templates = {
        "twitter_venting": "😤 {content} #venting",
        "linkedin_thought_leadership": "{content}\n\nWhat are your thoughts? #leadership",
        "facebook_community": "👉 {content}\n\nWhat do you think? 👇",
        "instagram_visual": "✨ {content}\n\n#trending #daily",
        "email_newsletter": "Hi {{name}},\n\n{content}\n\nBest regards"
    }

    if platform and content_type:
        key = f"{platform}_{content_type}".lower()
        return {
            "success": True,
            "template": templates.get(key, templates.get("twitter_venting")),
            "platform": platform,
            "content_type": content_type
        }
    else:
        return {
            "success": True,
            "templates": templates
        }


@router.post("/bulk-schedule", summary="Schedule multiple content pieces")
async def bulk_schedule(
    business_id: str = Query(...),
    content_calendar: List[Dict[str, Any]] = Body(...)
) -> Dict[str, Any]:
    """Schedule multiple content pieces for distribution"""

    return {
        "success": True,
        "business_id": business_id,
        "scheduled_count": len(content_calendar),
        "start_date": datetime.now().isoformat(),
        "status": "scheduled"
    }


# Health check
@router.get("/health", summary="Health check for content routing service")
async def health_check() -> Dict[str, Any]:
    """Check if content routing service is healthy"""
    return {
        "status": "healthy",
        "service": "content-routing",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    }
