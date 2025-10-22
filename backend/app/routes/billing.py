"""Token Usage, Billing & Pricing Tier API Routes"""
import logging
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional

from ..models.token_ledger import TokenLedger
from ..db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["billing"])


# ============================================================================
# Token Ledger Models
# ============================================================================

PRICING_TIERS = {
    "basic": {
        "name": "Basic",
        "price_usd": 20.00,
        "price_inr": 2000,
        "max_icps": 3,
        "max_moves": 5,
        "daily_token_limit": 50000,
        "monthly_token_limit": 1000000,
    },
    "pro": {
        "name": "Professional",
        "price_usd": 35.00,
        "price_inr": 3500,
        "max_icps": 6,
        "max_moves": 15,
        "daily_token_limit": 150000,
        "monthly_token_limit": 3000000,
    },
    "enterprise": {
        "name": "Enterprise",
        "price_usd": 50.00,
        "price_inr": 5000,
        "max_icps": 9,
        "max_moves": 999,
        "daily_token_limit": 500000,
        "monthly_token_limit": 10000000,
    },
}

# Store tier selection in memory (in production, use database)
USER_TIER_SELECTION = {}


# ============================================================================
# Token Usage Tracking
# ============================================================================

@router.get("/token-usage")
async def get_token_usage(
    strategy_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """
    Get token usage for current user

    Returns:
    - Total tokens used
    - Estimated cost
    - Daily/monthly remaining
    - Budget warnings
    - Cost breakdown by agent
    """
    try:
        # Calculate token usage
        query = db.query(
            func.sum(TokenLedger.tokens_used).label("total_tokens"),
            func.sum(TokenLedger.cost_usd).label("estimated_cost"),
            func.count(TokenLedger.id).label("calls_made"),
            func.count(TokenLedger.id).filter(TokenLedger.cached == True).label("cache_hits"),
        )

        if strategy_id:
            query = query.filter(TokenLedger.strategy_id == strategy_id)
        else:
            query = query.filter(TokenLedger.user_id == user_id)

        result = query.first()

        total_tokens = result.total_tokens or 0
        estimated_cost = result.estimated_cost or 0
        calls_made = result.calls_made or 0
        cache_hits = result.cache_hits or 0

        # Get user tier (default: basic)
        tier = USER_TIER_SELECTION.get(user_id, "basic")
        tier_config = PRICING_TIERS[tier]

        # Calculate daily/monthly usage
        today = datetime.now().date()
        month_start = datetime.now().replace(day=1).date()

        daily_query = db.query(func.sum(TokenLedger.tokens_used)).filter(
            TokenLedger.user_id == user_id,
            func.date(TokenLedger.created_at) == today
        )
        if strategy_id:
            daily_query = daily_query.filter(TokenLedger.strategy_id == strategy_id)
        daily_tokens = daily_query.scalar() or 0

        monthly_query = db.query(func.sum(TokenLedger.tokens_used)).filter(
            TokenLedger.user_id == user_id,
            func.date(TokenLedger.created_at) >= month_start
        )
        if strategy_id:
            monthly_query = monthly_query.filter(TokenLedger.strategy_id == strategy_id)
        monthly_tokens = monthly_query.scalar() or 0

        # Calculate remaining
        daily_limit = tier_config["daily_token_limit"]
        monthly_limit = tier_config["monthly_token_limit"]
        daily_remaining = max(0, daily_limit - daily_tokens)
        monthly_remaining = max(0, monthly_limit - monthly_tokens)

        # Calculate cost breakdown by agent
        agent_query = db.query(
            TokenLedger.agent_name,
            func.sum(TokenLedger.tokens_used).label("tokens"),
            func.sum(TokenLedger.cost_usd).label("cost")
        ).filter(TokenLedger.user_id == user_id)

        if strategy_id:
            agent_query = agent_query.filter(TokenLedger.strategy_id == strategy_id)

        agent_query = agent_query.group_by(TokenLedger.agent_name).all()

        tokens_by_agent = {agent.agent_name: agent.tokens for agent in agent_query}
        cost_by_agent = {agent.agent_name: agent.cost for agent in agent_query}

        # Check budget warnings/exceeded
        budget_exceeded = monthly_remaining <= 0
        budget_warning = (monthly_tokens / monthly_limit) > 0.8

        return {
            "data": {
                "session_tokens": total_tokens,
                "total_tokens": total_tokens,
                "estimated_cost": estimated_cost,
                "calls_made": calls_made,
                "cache_hits": cache_hits,
                "daily_limit": daily_limit,
                "monthly_limit": monthly_limit,
                "daily_remaining": daily_remaining,
                "monthly_remaining": monthly_remaining,
                "budget_exceeded": budget_exceeded,
                "budget_warning": budget_warning,
                "tokens_by_agent": tokens_by_agent,
                "cost_by_agent": cost_by_agent,
                "current_tier": tier,
            }
        }

    except Exception as e:
        logger.exception(f"Error getting token usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get token usage: {str(e)}"
        )


@router.get("/token-usage/{strategy_id}")
async def get_strategy_token_usage(
    strategy_id: str,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """
    Get token usage for specific strategy
    """
    try:
        return await get_token_usage(strategy_id=strategy_id, db=db, user_id=user_id)

    except Exception as e:
        logger.exception(f"Error getting strategy token usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get token usage: {str(e)}"
        )


# ============================================================================
# Budget Management
# ============================================================================

@router.get("/budget-status")
async def get_budget_status(
    db: Session = Depends(get_db),
    user_id: str = None
):
    """
    Get overall budget status and limits

    Returns:
    - Current month usage
    - Budget limit
    - Remaining budget
    - Warning/alert status
    - Projected month-end usage
    """
    try:
        # Get user tier (default: basic)
        tier = USER_TIER_SELECTION.get(user_id, "basic")
        tier_config = PRICING_TIERS[tier]

        # Calculate monthly usage
        month_start = datetime.now().replace(day=1).date()
        monthly_query = db.query(func.sum(TokenLedger.tokens_used)).filter(
            TokenLedger.user_id == user_id,
            func.date(TokenLedger.created_at) >= month_start
        )
        monthly_tokens = monthly_query.scalar() or 0

        # Calculate cost
        monthly_cost_query = db.query(func.sum(TokenLedger.cost_usd)).filter(
            TokenLedger.user_id == user_id,
            func.date(TokenLedger.created_at) >= month_start
        )
        monthly_cost = monthly_cost_query.scalar() or 0.0

        # Calculate monthly limit
        monthly_limit = tier_config["monthly_token_limit"]
        monthly_budget_usd = tier_config["price_usd"]
        remaining_tokens = max(0, monthly_limit - monthly_tokens)
        remaining_budget_usd = max(0, monthly_budget_usd - monthly_cost)

        # Calculate days remaining in month
        today = datetime.now().date()
        days_remaining = (datetime(today.year, today.month + 1 if today.month < 12 else 1, 1) - datetime.now()).days

        # Estimate month-end usage
        if days_remaining > 0 and today.day > 1:
            daily_usage = monthly_tokens / (today.day - 1)
            projected_total = monthly_tokens + (daily_usage * days_remaining)
        else:
            projected_total = monthly_tokens

        # Status
        status_text = "OK"
        if remaining_tokens <= 0:
            status_text = "EXCEEDED"
        elif (monthly_tokens / monthly_limit) > 0.9:
            status_text = "CRITICAL"
        elif (monthly_tokens / monthly_limit) > 0.7:
            status_text = "WARNING"

        return {
            "data": {
                "tier": tier,
                "tier_name": tier_config["name"],
                "monthly_tokens_used": monthly_tokens,
                "monthly_token_limit": monthly_limit,
                "remaining_tokens": remaining_tokens,
                "monthly_cost_usd": round(monthly_cost, 4),
                "monthly_budget_usd": monthly_budget_usd,
                "remaining_budget_usd": round(remaining_budget_usd, 4),
                "days_remaining": max(0, days_remaining),
                "projected_total_tokens": int(projected_total),
                "status": status_text,
            }
        }

    except Exception as e:
        logger.exception(f"Error getting budget status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get budget status: {str(e)}"
        )


# ============================================================================
# Subscription & Tier Management
# ============================================================================

@router.get("/subscription/tier")
async def get_subscription_tier(
    user_id: str = None
):
    """
    Get current subscription tier

    Returns tier info, limits, and features
    """
    try:
        tier = USER_TIER_SELECTION.get(user_id, "basic")
        tier_config = PRICING_TIERS[tier]

        return {
            "data": {
                "tier": tier,
                "name": tier_config["name"],
                "price_usd": tier_config["price_usd"],
                "price_inr": tier_config["price_inr"],
                "max_icps": tier_config["max_icps"],
                "max_moves": tier_config["max_moves"],
                "daily_limit": tier_config["daily_token_limit"],
                "monthly_limit": tier_config["monthly_token_limit"],
            }
        }

    except Exception as e:
        logger.exception(f"Error getting subscription tier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription tier: {str(e)}"
        )


@router.get("/features")
async def get_feature_flags(
    user_id: str = None
):
    """
    Get feature flags based on current tier

    Returns which features are available
    """
    try:
        tier = USER_TIER_SELECTION.get(user_id, "basic")

        features = {
            "basic": {
                "real_time_monitoring": True,
                "token_tracking": True,
                "basic_analytics": True,
                "email_support": True,
                "api_access": False,
                "custom_integrations": False,
                "team_collaboration": False,
            },
            "pro": {
                "real_time_monitoring": True,
                "token_tracking": True,
                "basic_analytics": True,
                "advanced_analytics": True,
                "email_support": True,
                "priority_support": True,
                "api_access": True,
                "custom_integrations": False,
                "team_collaboration": True,
            },
            "enterprise": {
                "real_time_monitoring": True,
                "token_tracking": True,
                "basic_analytics": True,
                "advanced_analytics": True,
                "email_support": True,
                "priority_support": True,
                "24_7_support": True,
                "api_access": True,
                "custom_integrations": True,
                "team_collaboration": True,
                "sso": True,
                "custom_slas": True,
            },
        }

        return {
            "data": {
                "tier": tier,
                "features": features.get(tier, features["basic"]),
            }
        }

    except Exception as e:
        logger.exception(f"Error getting feature flags: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feature flags: {str(e)}"
        )


# ============================================================================
# Development Mode Endpoints (Dev/Testing Only)
# ============================================================================

@router.post("/dev/set-tier")
async def set_pricing_tier(
    payload: dict,
    user_id: str = None
):
    """
    Set pricing tier for testing (DEV MODE ONLY)

    This endpoint is for development/testing purposes only.
    In production, tier changes go through billing system.

    Allowed tiers: 'basic', 'pro', 'enterprise'
    """
    try:
        tier = payload.get("tier", "basic")

        if tier not in PRICING_TIERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier. Must be one of: {list(PRICING_TIERS.keys())}"
            )

        # Store tier selection
        USER_TIER_SELECTION[user_id] = tier

        logger.info(f"Tier set to {tier} for user {user_id}")

        return {
            "data": {
                "tier": tier,
                "tier_name": PRICING_TIERS[tier]["name"],
                "message": f"Tier changed to {PRICING_TIERS[tier]['name']}"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error setting tier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set tier: {str(e)}"
        )


@router.get("/dev/current-tier")
async def get_current_tier(
    user_id: str = None
):
    """
    Get current tier selection (DEV MODE)
    """
    try:
        tier = USER_TIER_SELECTION.get(user_id, "basic")

        return {
            "data": {
                "tier": tier,
                "tier_name": PRICING_TIERS[tier]["name"],
                "config": PRICING_TIERS[tier],
            }
        }

    except Exception as e:
        logger.exception(f"Error getting current tier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current tier: {str(e)}"
        )


@router.get("/dev/available-tiers")
async def get_available_tiers():
    """
    Get all available tiers (DEV MODE)
    """
    try:
        return {
            "data": PRICING_TIERS
        }

    except Exception as e:
        logger.exception(f"Error getting available tiers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available tiers: {str(e)}"
        )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/health/db")
async def health_check_db(db: Session = Depends(get_db)):
    """
    Database health check
    """
    try:
        # Try a simple query
        db.execute("SELECT 1")
        return {
            "status": "ok",
            "service": "database",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {str(e)}"
        )


@router.get("/health/redis")
async def health_check_redis():
    """
    Redis health check (stub for future implementation)
    """
    return {
        "status": "ok",
        "service": "redis",
        "timestamp": datetime.now().isoformat(),
    }
