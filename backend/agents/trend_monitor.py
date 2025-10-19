from tools.perplexity_search import PerplexitySearchTool
from tools.relevance_scorer import RelevanceScorerTool
from tools.calendar_injector import CalendarInjectorTool
from utils.supabase_client import get_supabase_client
import asyncio
from datetime import datetime
import json

class TrendMonitorAgent:
    def __init__(self):
        self.perplexity = PerplexitySearchTool()
        self.scorer = RelevanceScorerTool()
        self.injector = CalendarInjectorTool()
        self.supabase = get_supabase_client()
    
    async def run_daily_monitoring(self):
        """Main async function to run daily"""
        print(f"[{datetime.utcnow()}] Starting daily trend monitoring...")
        
        # Get all active businesses with trend monitoring enabled
        businesses = self.supabase.table('subscriptions')\
            .select('business_id, tier')\
            .eq('status', 'active')\
            .in_('tier', ['pro', 'enterprise'])\
            .execute()
        
        for biz in businesses.data:
            business_id = biz['business_id']
            
            try:
                await self._monitor_business(business_id)
            except Exception as e:
                print(f"Error monitoring business {business_id}: {e}")
            
            # Rate limiting
            await asyncio.sleep(2)
        
        print(f"[{datetime.utcnow()}] Daily trend monitoring complete.")
    
    async def _monitor_business(self, business_id: str):
        """Monitor trends for a single business"""
        # Get all ICPs
        icps = self.supabase.table('icps')\
            .select('*')\
            .eq('business_id', business_id)\
            .execute()
        
        for icp in icps.data:
            tags = icp['monitoring_tags']
            
            # Search Perplexity for trends
            search_query = f"Latest trends and news about: {', '.join(tags[:5])}"
            
            trends_result = await self.perplexity._arun(
                query=search_query,
                mode='trends',
                recency='day'
            )
            
            trends_data = json.loads(trends_result)
            
            # Parse trends from findings
            trends = self._parse_trends(trends_data['findings'])
            
            # Score each trend for relevance
            relevant_trends = []
            
            for trend in trends:
                score_result = self.scorer._run(
                    trend=trend,
                    icp=icp
                )
                
                score_data = json.loads(score_result)
                
                if score_data['should_use']:
                    relevant_trends.append({
                        'trend': trend,
                        'score_data': score_data
                    })
            
            # Inject high-relevance trends into calendar
            if relevant_trends:
                # Get active moves for this business
                moves = self.supabase.table('moves')\
                    .select('id')\
                    .eq('business_id', business_id)\
                    .eq('status', 'active')\
                    .execute()
                
                if moves.data:
                    move_id = moves.data[0]['id']
                    
                    # Inject top trend
                    top_trend = relevant_trends[0]
                    
                    self.injector._run(
                        move_id=move_id,
                        trend=top_trend['trend'],
                        icp=icp
                    )
            
            # Save to trend_checks table
            self.supabase.table('trend_checks').insert({
                'business_id': business_id,
                'icp_id': icp['id'],
                'search_tags': tags,
                'trends_found': [t['trend'] for t in relevant_trends],
                'relevance_scores': [t['score_data']['combined_score'] for t in relevant_trends],
                'calendar_injected': len(relevant_trends) > 0
            }).execute()
    
    def _parse_trends(self, findings_text: str) -> List[Dict]:
        """Parse trends from Perplexity response"""
        # Simple parsing - in production, use better extraction
        trends = []
        
        lines = findings_text.split('\n')
        for line in lines:
            if line.strip() and len(line) > 20:
                trends.append({
                    'title': line[:100],
                    'description': line
                })
        
        return trends[:5]  # Top 5 trends

# Create singleton
trend_monitor = TrendMonitorAgent()
