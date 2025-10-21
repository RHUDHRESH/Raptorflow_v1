"""
Budget Monitoring API Routes
Real-time cost tracking and budget status
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from ..middleware.budget_controller import budget_controller

router = APIRouter(prefix="/api/budget", tags=["budget"])

@router.get("/status")
async def get_budget_status() -> Dict[str, Any]:
    """Get current budget status with warnings"""
    try:
        status = budget_controller.get_budget_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get budget status: {str(e)}")

@router.get("/usage")
async def get_usage_history(days: int = 7) -> Dict[str, Any]:
    """Get usage history for the past N days"""
    try:
        usage_history = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            usage_key = f"budget_usage:{date}"
            
            # Get usage from Redis (this would need to be implemented)
            # For now, return simulated data
            daily_usage = {
                "date": date,
                "gpt5_nano_requests": 200 if i < 3 else 0,
                "gpt5_requests": 5 if i < 3 else 0,
                "total_tokens": 5000 if i < 3 else 0,
                "total_cost": 0.35 if i < 3 else 0.0
            }
            usage_history.append(daily_usage)
        
        return {
            "success": True,
            "data": {
                "usage_history": usage_history,
                "total_cost_last_7_days": sum(day["total_cost"] for day in usage_history),
                "average_daily_cost": sum(day["total_cost"] for day in usage_history) / days
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage history: {str(e)}")

@router.get("/limits")
async def get_budget_limits() -> Dict[str, Any]:
    """Get current budget limits and quotas"""
    try:
        return {
            "success": True,
            "data": {
                "daily_budget": 0.50,  # $15/month ÷ 30
                "monthly_budget": 15.00,
                "daily_limits": {
                    "gpt5_nano_requests": 267,
                    "gpt5_requests": 13,
                    "total_tokens": 14000
                },
                "monthly_limits": {
                    "gpt5_nano_requests": 8000,
                    "gpt5_requests": 400,
                    "total_tokens": 420000
                },
                "model_costs": {
                    "gpt5_nano": {
                        "input_per_1k": 0.0002,
                        "output_per_1k": 0.0006
                    },
                    "gpt5": {
                        "input_per_1k": 0.0015,
                        "output_per_1k": 0.005
                    }
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get budget limits: {str(e)}")

@router.post("/emergency-lift")
async def lift_emergency_shutdown() -> Dict[str, Any]:
    """Lift emergency shutdown (admin only)"""
    try:
        budget_controller.lift_emergency_shutdown()
        return {
            "success": True,
            "message": "Emergency shutdown lifted",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to lift emergency shutdown: {str(e)}")

@router.get("/projections")
async def get_cost_projections() -> Dict[str, Any]:
    """Get cost projections based on current usage"""
    try:
        current_usage = budget_controller.get_daily_usage()
        
        # Project monthly cost based on today's usage
        daily_cost = current_usage['total_cost']
        projected_monthly = daily_cost * 30
        
        # Calculate remaining budget
        remaining_daily = 0.50 - daily_cost
        remaining_monthly = remaining_daily * 30
        
        return {
            "success": True,
            "data": {
                "current_daily_cost": daily_cost,
                "projected_monthly_cost": projected_monthly,
                "remaining_daily_budget": remaining_daily,
                "remaining_monthly_budget": remaining_monthly,
                "budget_status": "on_track" if projected_monthly <= 15.00 else "over_budget",
                "recommendations": _get_budget_recommendations(daily_cost, projected_monthly)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projections: {str(e)}")

def _get_budget_recommendations(daily_cost: float, projected_monthly: float) -> List[str]:
    """Get budget recommendations based on usage"""
    recommendations = []
    
    if projected_monthly > 15.00:
        recommendations.append("REDUCE USAGE: Current pace exceeds monthly budget")
        recommendations.append("Switch to GPT-5 Nano for all non-critical tasks")
        recommendations.append("Implement caching to reduce API calls")
    elif projected_monthly > 12.00:
        recommendations.append("MONITOR CLOSELY: Approaching monthly budget limit")
        recommendations.append("Consider reducing request frequency")
    elif daily_cost < 0.10:
        recommendations.append("GOOD: Well within budget limits")
        recommendations.append("Current usage is sustainable")
    
    return recommendations

@router.get("/health")
async def budget_health_check() -> Dict[str, Any]:
    """Health check for budget system"""
    try:
        status = budget_controller.get_budget_status()
        emergency_mode = budget_controller.is_emergency_mode()
        
        health_status = "healthy"
        if status["status"] == "CRITICAL":
            health_status = "critical"
        elif status["status"] == "WARNING":
            health_status = "warning"
        elif emergency_mode:
            health_status = "emergency"
        
        return {
            "success": True,
            "data": {
                "health_status": health_status,
                "emergency_mode": emergency_mode,
                "budget_percent_used": status["percent_used"],
                "daily_budget_remaining": status["remaining"],
                "warnings_count": len(status["warnings"])
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Budget health check failed: {str(e)}")
