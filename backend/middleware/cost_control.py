from datetime import datetime, timedelta
from utils.supabase_client import get_supabase_client
from typing import Dict

class CostControlGuardrails:
    """Prevent runaway costs from API usage"""
    
    # Cost per 1K tokens (in )
    API_COSTS = {
        'gemini_2_flash': 0.075,  # 0.075 per 1K tokens
        'perplexity': 0.5,         # 0.50 per search
        'openai_embeddings': 0.02  # 0.02 per 1K tokens
    }
    
    # Monthly budgets by tier (in )
    MONTHLY_BUDGETS = {
        'basic': 500,
        'pro': 2000,
        'enterprise': 10000
    }
    
    @staticmethod
    async def check_budget(business_id: str, tier: str) -> Dict:
        """Check if business has budget remaining"""
        
        supabase = get_supabase_client()
        
        # Get current month spending
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        
        result = supabase.table('api_usage')\
            .select('*')\
            .eq('business_id', business_id)\
            .gte('created_at', start_of_month.isoformat())\
            .execute()
        
        # Calculate total cost
        total_cost = sum(
            CostControlGuardrails.calculate_cost(record)
            for record in result.data
        )
        
        budget = CostControlGuardrails.MONTHLY_BUDGETS[tier]
        remaining = budget - total_cost
        
        if remaining <= 0:
            raise HTTPException(
                status_code=402,  # Payment Required
                detail={
                    'error': 'Monthly budget exceeded',
                    'total_spent': total_cost,
                    'budget': budget,
                    'tier': tier,
                    'message': 'Please upgrade your plan or wait until next month'
                }
            )
        
        # Warning at 80%
        if remaining < budget * 0.2:
            return {
                'warning': True,
                'remaining': remaining,
                'budget': budget,
                'percentage_used': (total_cost / budget) * 100
            }
        
        return {
            'ok': True,
            'remaining': remaining,
            'budget': budget
        }
    
    @staticmethod
    def calculate_cost(api_record: Dict) -> float:
        """Calculate cost from API usage record"""
        
        api_type = api_record['api_type']
        
        if api_type == 'gemini':
            tokens = api_record.get('tokens', 0)
            return (tokens / 1000) * CostControlGuardrails.API_COSTS['gemini_2_flash']
        
        elif api_type == 'perplexity':
            calls = api_record.get('calls', 1)
            return calls * CostControlGuardrails.API_COSTS['perplexity']
        
        elif api_type == 'openai_embeddings':
            tokens = api_record.get('tokens', 0)
            return (tokens / 1000) * CostControlGuardrails.API_COSTS['openai_embeddings']
        
        return 0
    
    @staticmethod
    async def track_usage(
        business_id: str,
        api_type: str,
        tokens: int = 0,
        calls: int = 1
    ):
        """Track API usage for cost monitoring"""
        
        supabase = get_supabase_client()
        
        cost = CostControlGuardrails.calculate_cost({
            'api_type': api_type,
            'tokens': tokens,
            'calls': calls
        })
        
        supabase.table('api_usage').insert({
            'business_id': business_id,
            'api_type': api_type,
            'tokens': tokens,
            'calls': calls,
            'cost': cost,
            'created_at': datetime.utcnow().isoformat()
        }).execute()

# Decorator for cost tracking
def track_cost(api_type: str):
    """Decorator to track API costs"""
    async def decorator(func):
        async def wrapper(*args, **kwargs):
            business_id = kwargs.get('business_id')
            
            # Get tier and check budget
            from utils.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            sub = supabase.table('subscriptions')\
                .select('tier')\
                .eq('business_id', business_id)\
                .single()\
                .execute()
            
            tier = sub.data['tier'] if sub.data else 'basic'
            await CostControlGuardrails.check_budget(business_id, tier)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Track usage (estimate tokens)
            tokens = kwargs.get('tokens', 1000)  # Default estimate
            await CostControlGuardrails.track_usage(
                business_id,
                api_type,
                tokens=tokens
            )
            
            return result
        return wrapper
    return decorator
