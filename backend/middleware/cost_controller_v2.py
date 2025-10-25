"""
Cost Controller v2: Tier-Based Budget Enforcement

Implements subscription tier-based daily/monthly budget limits with:
- Real-time cost tracking
- Emergency shutdown at limit exceeded
- Progressive warnings (75%, 90%, 100%)
- Cost projections and usage analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BudgetTier(BaseModel):
    """Subscription tier budget configuration"""
    name: str
    daily_limit: float  # USD
    monthly_limit: float  # USD
    max_icps: int
    max_moves: int
    model_priority: str  # "nano_only", "nano_mini", "full"


class CostController:
    """
    Enforce tier-based daily budget limits with automatic shutdown.

    Tier Limits:
    - Basic: $10/day, 3 ICPs, 5 moves
    - Pro: $50/day, 6 ICPs, 15 moves
    - Enterprise: $200/day, 9 ICPs, 999 moves
    """

    TIER_LIMITS = {
        "basic": BudgetTier(
            name="basic",
            daily_limit=10.00,
            monthly_limit=300.00,
            max_icps=3,
            max_moves=5,
            model_priority="nano_mini"  # No GPT-5, only nano and mini
        ),
        "pro": BudgetTier(
            name="pro",
            daily_limit=50.00,
            monthly_limit=1500.00,
            max_icps=6,
            max_moves=15,
            model_priority="nano_mini"  # Still limited to nano/mini
        ),
        "enterprise": BudgetTier(
            name="enterprise",
            daily_limit=200.00,
            monthly_limit=6000.00,
            max_icps=9,
            max_moves=999,
            model_priority="full"  # Full access to all models
        ),
    }

    def __init__(self, ai_provider_manager, supabase_client):
        """
        Initialize Cost Controller.

        Args:
            ai_provider_manager: AIProviderManager instance
            supabase_client: Supabase client for querying subscription data
        """
        self.ai = ai_provider_manager
        self.db = supabase_client
        self._budget_cache: Dict[str, Dict] = {}  # Cache budget status

    async def check_budget_before_task(
        self,
        business_id: str,
        task_type: str,
        input_length: int,
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if business has budget remaining for task.

        Returns:
            (can_proceed: bool, budget_info: dict)
        """
        # Get subscription tier
        subscription = await self._get_subscription(business_id)
        tier = subscription["tier"]
        tier_config = self.TIER_LIMITS[tier]

        # Get today's spending from AI provider manager
        today_cost = self.ai.get_daily_cost(datetime.utcnow())

        # Estimate cost for this task
        estimated_cost = self.ai.estimate_task_cost(task_type, input_length)

        # Check model tier restrictions
        model_for_task = self.ai.TASK_ROUTING.get(task_type, "gpt-5-mini")
        if tier_config.model_priority == "nano_only" and model_for_task != "gpt-5-nano":
            logger.warning(
                f"❌ Task {task_type} requires {model_for_task} but {tier} tier only allows nano"
            )
            return False, {
                "reason": "model_tier_restricted",
                "allowed": "gpt-5-nano",
                "required": model_for_task,
            }

        if tier_config.model_priority == "nano_mini" and model_for_task == "gpt-5":
            logger.warning(
                f"❌ Task {task_type} requires GPT-5 but {tier} tier only allows nano/mini"
            )
            return False, {
                "reason": "model_tier_restricted",
                "allowed": "gpt-5-nano, gpt-5-mini",
                "required": model_for_task,
            }

        # Check daily budget
        if today_cost + estimated_cost > tier_config.daily_limit:
            logger.warning(
                f"❌ Daily budget exceeded for {business_id} | "
                f"Tier: {tier} | Limit: ${tier_config.daily_limit:.2f} | "
                f"Spent: ${today_cost:.2f} | Estimated task: ${estimated_cost:.2f}"
            )
            return False, {
                "reason": "daily_budget_exceeded",
                "tier": tier,
                "limit": tier_config.daily_limit,
                "spent_today": today_cost,
                "estimated_task": estimated_cost,
                "remaining": max(0, tier_config.daily_limit - today_cost),
            }

        # Generate budget info
        budget_info = {
            "can_proceed": True,
            "tier": tier,
            "daily_limit": tier_config.daily_limit,
            "spent_today": today_cost,
            "estimated_task": estimated_cost,
            "remaining": tier_config.daily_limit - (today_cost + estimated_cost),
            "usage_percent": (today_cost / tier_config.daily_limit) * 100,
        }

        # Warning at 75%
        if budget_info["usage_percent"] >= 75:
            severity = "warning"
            if budget_info["usage_percent"] >= 90:
                severity = "critical"
            logger.warning(
                f"⚠️ [{severity}] Budget warning for {business_id}: "
                f"{budget_info['usage_percent']:.1f}% of daily limit used"
            )
            budget_info["warning"] = severity

        return True, budget_info

    async def track_cost(
        self,
        business_id: str,
        cost: float,
        model_used: str,
        task_type: str
    ) -> None:
        """
        Track cost for a completed task.

        This should be called after task completes with actual cost.

        Args:
            business_id: Business ID
            cost: Actual cost in USD
            model_used: Which model was used
            task_type: Type of task
        """
        # Log to usage tracking
        logger.info(
            f"Cost tracked for {business_id}: ${cost:.4f} | "
            f"Model: {model_used} | Task: {task_type}"
        )

        # Could optionally save to database for audit trail
        # await self.db.table("cost_tracking").insert({...}).execute()

    async def get_budget_status(self, business_id: str) -> Dict:
        """
        Get current budget status for a business.

        Returns:
            {
                "tier": str,
                "daily_limit": float,
                "monthly_limit": float,
                "spent_today": float,
                "spent_this_month": float,
                "remaining_today": float,
                "remaining_month": float,
                "usage_today_percent": float,
                "usage_month_percent": float,
                "days_remaining": int,
                "projected_month_cost": float,
            }
        """
        subscription = await self._get_subscription(business_id)
        tier = subscription["tier"]
        tier_config = self.TIER_LIMITS[tier]

        # Get today and this month costs
        today = datetime.utcnow()
        spent_today = self.ai.get_daily_cost(today)

        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        spent_month = sum(
            record.total_cost
            for record in self.ai.usage_log
            if month_start <= record.timestamp < month_end
        )

        # Calculate projections
        days_into_month = today.day
        projected_month_cost = (spent_month / days_into_month) * 30

        days_remaining = 30 - days_into_month

        return {
            "tier": tier,
            "daily_limit": tier_config.daily_limit,
            "monthly_limit": tier_config.monthly_limit,
            "spent_today": round(spent_today, 4),
            "spent_this_month": round(spent_month, 4),
            "remaining_today": round(max(0, tier_config.daily_limit - spent_today), 4),
            "remaining_month": round(max(0, tier_config.monthly_limit - spent_month), 4),
            "usage_today_percent": round((spent_today / tier_config.daily_limit) * 100, 2),
            "usage_month_percent": round((spent_month / tier_config.monthly_limit) * 100, 2),
            "days_remaining": days_remaining,
            "projected_month_cost": round(projected_month_cost, 2),
            "on_track": projected_month_cost <= tier_config.monthly_limit,
        }

    async def get_usage_history(self, business_id: str, days: int = 7) -> Dict:
        """
        Get usage history for last N days.

        Returns:
            {
                "dates": [date, ...],
                "daily_costs": [cost, ...],
                "daily_requests": [count, ...],
                "average_cost_per_request": float,
            }
        """
        subscription = await self._get_subscription(business_id)
        tier_config = self.TIER_LIMITS[subscription["tier"]]

        today = datetime.utcnow().date()
        daily_costs = {}
        daily_requests = {}

        # Build cost and request counts for each day
        for i in range(days):
            date = today - timedelta(days=i)
            date_obj = datetime.combine(date, datetime.min.time())
            daily_cost = self.ai.get_daily_cost(date_obj)
            daily_costs[date] = daily_cost

            # Count requests for this day
            request_count = sum(
                1 for record in self.ai.usage_log
                if record.timestamp.date() == date
            )
            daily_requests[date] = request_count

        # Sort by date (oldest first)
        sorted_dates = sorted(daily_costs.keys())

        total_requests = sum(daily_requests.values())
        total_cost = sum(daily_costs.values())
        avg_cost_per_request = (total_cost / total_requests) if total_requests > 0 else 0

        return {
            "dates": [str(d) for d in sorted_dates],
            "daily_costs": [daily_costs[d] for d in sorted_dates],
            "daily_requests": [daily_requests[d] for d in sorted_dates],
            "total_cost": round(total_cost, 4),
            "total_requests": total_requests,
            "average_cost_per_request": round(avg_cost_per_request, 4),
            "tier": subscription["tier"],
            "tier_limit": tier_config.daily_limit,
        }

    async def get_feature_limits(self, business_id: str) -> Dict:
        """
        Get feature usage limits for subscription tier.

        Returns:
            {
                "tier": str,
                "max_icps": int,
                "max_moves": int,
                "current_icps": int,
                "current_moves": int,
                "icps_remaining": int,
                "moves_remaining": int,
            }
        """
        subscription = await self._get_subscription(business_id)
        tier_config = self.TIER_LIMITS[subscription["tier"]]

        # Get current usage
        icps = self.db.table("icps") \
            .select("count") \
            .eq("business_id", business_id) \
            .execute()
        current_icps = icps.count

        moves = self.db.table("moves") \
            .select("count") \
            .eq("business_id", business_id) \
            .execute()
        current_moves = moves.count

        return {
            "tier": subscription["tier"],
            "max_icps": tier_config.max_icps,
            "max_moves": tier_config.max_moves,
            "current_icps": current_icps,
            "current_moves": current_moves,
            "icps_remaining": max(0, tier_config.max_icps - current_icps),
            "moves_remaining": max(0, tier_config.max_moves - current_moves),
            "icps_usage_percent": round((current_icps / tier_config.max_icps) * 100, 2),
            "moves_usage_percent": round((current_moves / tier_config.max_moves) * 100, 2),
        }

    async def _get_subscription(self, business_id: str) -> Dict:
        """Get subscription for business."""
        if business_id in self._budget_cache:
            # Use cache (refreshed daily)
            cached = self._budget_cache[business_id]
            if cached["cached_at"] > datetime.utcnow() - timedelta(hours=1):
                return cached["data"]

        result = self.db.table("subscriptions") \
            .select("*") \
            .eq("business_id", business_id) \
            .single() \
            .execute()

        if not result.data:
            raise ValueError(f"Subscription not found for business {business_id}")

        # Cache the result
        self._budget_cache[business_id] = {
            "data": result.data,
            "cached_at": datetime.utcnow()
        }

        return result.data


class CostLimitExceeded(Exception):
    """Raised when cost limit exceeded for a tier"""
    pass
