from langchain.tools import BaseTool
from utils.supabase_client import get_supabase_client
from utils.gemini_client import get_gemini_client
import json
from datetime import datetime, timedelta

class CalendarInjectorTool(BaseTool):
    name = "calendar_injector"
    description = """
    Inject trending topics into existing content calendar.
    
    Rules:
    - Don't disrupt planned sequence
    - Maintain 4:1 value ratio
    - Find best insertion point
    - Generate trend-based content
    
    Examples:
    calendar_injector(move_id='uuid', trend={...}, icp={...})
    """
    
    def __init__(self):
        super().__init__()
        self.supabase = get_supabase_client()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        move_id: str,
        trend: Dict,
        icp: Dict
    ) -> str:
        
        # Get existing calendar
        move = self.supabase.table('moves')\
            .select('*')\
            .eq('id', move_id)\
            .single()\
            .execute()
        
        calendar = move.data['calendar']
        platform = move.data['platform']
        
        # Generate trend-based content
        prompt = f"""Create content that leverages this trend for {platform}.

TREND:
{json.dumps(trend, indent=2)}

ICP:
{json.dumps(icp, indent=2)}

PLATFORM: {platform}

Create a {platform} post that:
1. References the trend naturally
2. Connects to ICP interests
3. Provides value (not just jumping on trend)
4. Includes clear CTA
5. Follows {platform} best practices

Return JSON:
{{
  "post": {{
    "text": "Full post text",
    "hook": "First line",
    "trend_reference": "How we reference the trend",
    "value_add": "What value we provide beyond the trend",
    "cta": "Call to action",
    "hashtags": ["..."],
    "content_type": "educational|entertaining|inspirational",
    "estimated_engagement": "high|medium|low"
  }},
  "insertion_strategy": "beginning|middle|end",
  "rationale": "Why insert here"
}}"""
        
        response = self.gemini.generate_content(prompt)
        result = json.loads(response.text)
        
        # Find best insertion point
        insertion_day = self._find_insertion_point(
            calendar,
            result['insertion_strategy']
        )
        
        # Create new post entry
        new_post = {
            'time': '10:00',  # Default optimal time
            'race_phase': 'reach',  # Trends usually for awareness
            'icp_target': icp['name'],
            'content_type': result['post']['content_type'],
            'format': 'text',
            'text': result['post']['text'],
            'hook': result['post']['hook'],
            'cta': result['post']['cta'],
            'hashtags': result['post']['hashtags'],
            'trend_based': True,
            'trend_info': {
                'trend_title': trend.get('title'),
                'injected_at': datetime.utcnow().isoformat()
            }
        }
        
        # Insert into calendar
        if insertion_day < len(calendar['calendar']):
            calendar['calendar'][insertion_day]['posts'].append(new_post)
        else:
            # Add new day if needed
            calendar['calendar'].append({
                'day': len(calendar['calendar']) + 1,
                'posts': [new_post]
            })
        
        # Update move in database
        self.supabase.table('moves')\
            .update({'calendar': calendar})\
            .eq('id', move_id)\
            .execute()
        
        return json.dumps({
            'success': True,
            'move_id': move_id,
            'injected_post': new_post,
            'insertion_day': insertion_day + 1,
            'insertion_strategy': result['insertion_strategy'],
            'rationale': result['rationale']
        })
    
    def _find_insertion_point(self, calendar, strategy):
        total_days = len(calendar.get('calendar', []))
        
        if strategy == 'beginning':
            return 0
        elif strategy == 'end':
            return total_days - 1
        else:  # middle
            return total_days // 2
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
