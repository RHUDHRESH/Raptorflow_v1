"""
BUDGET CONTROLLER - ENFORCES $10-15 MONTHLY LIMIT
CRITICAL: Prevents overspending on AI APIs
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import redis
import os

@dataclass
class APICost:
    """Cost per 1K tokens for different models"""
    # GPT-5 Nano (Primary Model - CHEAPEST)
    GPT5_NANO_INPUT = 0.0002  # $0.0002 per 1K input tokens
    GPT5_NANO_OUTPUT = 0.0006  # $0.0006 per 1K output tokens
    
    # GPT-5 (Reasoning Model - LIMITED USE)
    GPT5_INPUT = 0.0015  # $0.0015 per 1K input tokens
    GPT5_OUTPUT = 0.005  # $0.005 per 1K output tokens

@dataclass
class DailyLimits:
    """Daily limits to stay under $15/month"""
    DAILY_BUDGET = 0.50  # $15/month ÷ 30 days
    GPT5_NANO_REQUESTS = 267  # 8,000/month ÷ 30
    GPT5_REQUESTS = 13  # 400/month ÷ 30
    TOTAL_TOKENS_PER_DAY = 14000

class BudgetController:
    """HARD ENFORCER of budget limits"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.limits = DailyLimits()
        self.costs = APICost()
        
    def get_daily_usage(self) -> Dict:
        """Get today's usage statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        usage_key = f"budget_usage:{today}"
        
        usage = self.redis_client.hgetall(usage_key)
        if not usage:
            return {
                'gpt5_nano_requests': 0,
                'gpt5_requests': 0,
                'total_tokens': 0,
                'total_cost': 0.0
            }
        
        return {
            'gpt5_nano_requests': int(usage.get('gpt5_nano_requests', 0)),
            'gpt5_requests': int(usage.get('gpt5_requests', 0)),
            'total_tokens': int(usage.get('total_tokens', 0)),
            'total_cost': float(usage.get('total_cost', 0.0))
        }
    
    def calculate_request_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate exact cost for a request"""
        if model == "gpt-5-nano":
            input_cost = (input_tokens / 1000) * self.costs.GPT5_NANO_INPUT
            output_cost = (output_tokens / 1000) * self.costs.GPT5_NANO_OUTPUT
        elif model == "gpt-5":
            input_cost = (input_tokens / 1000) * self.costs.GPT5_INPUT
            output_cost = (output_tokens / 1000) * self.costs.GPT5_OUTPUT
        else:
            raise ValueError(f"Unknown model: {model}")
        
        return input_cost + output_cost
    
    def can_make_request(self, model: str, estimated_input_tokens: int = 400, estimated_output_tokens: int = 100) -> Tuple[bool, str]:
        """Check if request can be made within budget"""
        usage = self.get_daily_usage()
        estimated_cost = self.calculate_request_cost(model, estimated_input_tokens, estimated_output_tokens)
        
        # Check daily budget
        if usage['total_cost'] + estimated_cost > self.limits.DAILY_BUDGET:
            return False, f"Daily budget exceeded. Current: ${usage['total_cost']:.4f}, Limit: ${self.limits.DAILY_BUDGET}"
        
        # Check model-specific limits
        if model == "gpt-5-nano":
            if usage['gpt5_nano_requests'] >= self.limits.GPT5_NANO_REQUESTS:
                return False, f"GPT-5 Nano daily limit reached: {self.limits.GPT5_NANO_REQUESTS}"
        elif model == "gpt-5":
            if usage['gpt5_requests'] >= self.limits.GPT5_REQUESTS:
                return False, f"GPT-5 daily limit reached: {self.limits.GPT5_REQUESTS}"
        
        # Check total tokens
        total_tokens = usage['total_tokens'] + estimated_input_tokens + estimated_output_tokens
        if total_tokens > self.limits.TOTAL_TOKENS_PER_DAY:
            return False, f"Daily token limit exceeded: {self.limits.TOTAL_TOKENS_PER_DAY}"
        
        return True, "Request allowed"
    
    def get_cheapest_viable_model(self, task_complexity: str, estimated_tokens: int = 500) -> str:
        """Always choose cheapest model that can handle the task"""
        # Priority order: GPT-5 Nano (cheapest) -> GPT-5 (expensive)
        
        # First try GPT-5 Nano
        can_use_nano, reason = self.can_make_request("gpt-5-nano", estimated_tokens, estimated_tokens // 4)
        if can_use_nano:
            return "gpt-5-nano"
        
        # Only use GPT-5 if absolutely necessary and budget allows
        if task_complexity in ["complex_reasoning", "strategic_analysis"]:
            can_use_gpt5, reason = self.can_make_request("gpt-5", estimated_tokens, estimated_tokens // 3)
            if can_use_gpt5:
                return "gpt-5"
        
        # Emergency fallback
        return "gpt-5-nano"  # Force use even if over limit (better than nothing)
    
    def record_usage(self, model: str, input_tokens: int, output_tokens: int):
        """Record actual API usage"""
        today = datetime.now().strftime('%Y-%m-%d')
        usage_key = f"budget_usage:{today}"
        
        cost = self.calculate_request_cost(model, input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens
        
        # Update counters
        if model == "gpt-5-nano":
            self.redis_client.hincrby(usage_key, 'gpt5_nano_requests', 1)
        elif model == "gpt-5":
            self.redis_client.hincrby(usage_key, 'gpt5_requests', 1)
        
        self.redis_client.hincrby(usage_key, 'total_tokens', total_tokens)
        self.redis_client.hincrbyfloat(usage_key, 'total_cost', cost)
        
        # Set expiry for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        expiry_seconds = int((tomorrow_midnight - datetime.now()).total_seconds())
        self.redis_client.expire(usage_key, expiry_seconds)
    
    def get_budget_status(self) -> Dict:
        """Get current budget status with warnings"""
        usage = self.get_daily_usage()
        budget_used_percent = (usage['total_cost'] / self.limits.DAILY_BUDGET) * 100
        
        status = {
            'daily_budget': self.limits.DAILY_BUDGET,
            'used_today': usage['total_cost'],
            'remaining': self.limits.DAILY_BUDGET - usage['total_cost'],
            'percent_used': budget_used_percent,
            'status': 'OK',
            'warnings': [],
            'usage': usage
        }
        
        # Add warnings
        if budget_used_percent >= 90:
            status['status'] = 'CRITICAL'
            status['warnings'].append('CRITICAL: Almost out of budget!')
        elif budget_used_percent >= 75:
            status['status'] = 'WARNING'
            status['warnings'].append('WARNING: Using 75%+ of daily budget')
        elif budget_used_percent >= 50:
            status['warnings'].append('INFO: Using 50%+ of daily budget')
        
        # Check model limits
        if usage['gpt5_requests'] >= self.limits.GPT5_REQUESTS:
            status['warnings'].append('GPT-5 daily limit reached')
        
        if usage['gpt5_nano_requests'] >= self.limits.GPT5_NANO_REQUESTS:
            status['warnings'].append('GPT-5 Nano daily limit reached')
        
        return status
    
    def emergency_shutdown(self) -> bool:
        """Emergency shutdown when budget is exhausted"""
        usage = self.get_daily_usage()
        
        if usage['total_cost'] >= self.limits.DAILY_BUDGET:
            # Set emergency flag
            self.redis_client.set('budget_emergency_shutdown', '1', ex=86400)  # 24 hours
            return True
        return False
    
    def is_emergency_mode(self) -> bool:
        """Check if we're in emergency shutdown mode"""
        return self.redis_client.exists('budget_emergency_shutdown')
    
    def lift_emergency_shutdown(self):
        """Lift emergency shutdown (for new day)"""
        self.redis_client.delete('budget_emergency_shutdown')

# Global instance
budget_controller = BudgetController()

def check_budget_before_api_call(model: str, estimated_input_tokens: int = 400, estimated_output_tokens: int = 100):
    """Decorator to check budget before API calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check emergency mode
            if budget_controller.is_emergency_mode():
                return {
                    'error': 'BUDGET_EXHAUSTED',
                    'message': 'Daily budget exhausted. Please try again tomorrow.',
                    'status': 'emergency_shutdown'
                }
            
            # Check if request is allowed
            can_make, reason = budget_controller.can_make_request(model, estimated_input_tokens, estimated_output_tokens)
            if not can_make:
                return {
                    'error': 'BUDGET_LIMIT_EXCEEDED',
                    'message': reason,
                    'status': 'blocked'
                }
            
            # Make the API call
            try:
                result = func(*args, **kwargs)
                
                # Record usage if successful
                if hasattr(result, 'usage') or 'usage' in result:
                    usage_data = result.get('usage', {}) if isinstance(result, dict) else getattr(result, 'usage', {})
                    input_tokens = usage_data.get('prompt_tokens', estimated_input_tokens)
                    output_tokens = usage_data.get('completion_tokens', estimated_output_tokens)
                    budget_controller.record_usage(model, input_tokens, output_tokens)
                
                return result
                
            except Exception as e:
                # Don't record usage if API call failed
                return {
                    'error': 'API_CALL_FAILED',
                    'message': str(e),
                    'status': 'failed'
                }
        
        return wrapper
    return decorator

def get_optimal_model(task_complexity: str, estimated_tokens: int = 500) -> str:
    """Get the optimal model for a task within budget constraints"""
    return budget_controller.get_cheapest_viable_model(task_complexity, estimated_tokens)
