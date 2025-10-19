from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
from tools.platform_validator import PlatformValidatorTool
import json
from datetime import datetime, timedelta

class CalendarGeneratorTool(BaseTool):
    name = "calendar_generator"
    description = """
    Generate complete content calendar with platform-validated posts.
    
    Features:
    - Multi-day planning
    - Platform-specific formatting
    - RACE phase mapping
    - 4:1 value ratio (4 value posts : 1 promo)
    - Time optimization
    
    Examples:
    calendar_generator(duration_days=7, platform='twitter', goal='100 followers', icps=[...])
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
        self.validator = PlatformValidatorTool()
    
    def _run(
        self,
        duration_days: int,
        platform: str,
        goal: str,
        icps: List[Dict],
        positioning: Optional[Dict] = None,
        race_allocation: Optional[Dict] = None
    ) -> str:
        
        # Get platform specs
        specs = json.loads(self.validator._run(action='get_specs', platform=platform))['specs']
        
        # Default RACE allocation if not provided
        if not race_allocation:
            if duration_days <= 7:
                race_allocation = {
                    'reach': {'days': 2, 'percentage': 30},
                    'act': {'days': 3, 'percentage': 40},
                    'convert': {'days': 2, 'percentage': 30}
                }
            elif duration_days <= 14:
                race_allocation = {
                    'reach': {'days': 4, 'percentage': 30},
                    'act': {'days': 5, 'percentage': 35},
                    'convert': {'days': 4, 'percentage': 25},
                    'engage': {'days': 1, 'percentage': 10}
                }
            else:
                reach_days = int(duration_days * 0.25)
                act_days = int(duration_days * 0.35)
                convert_days = int(duration_days * 0.30)
                engage_days = duration_days - reach_days - act_days - convert_days
                
                race_allocation = {
                    'reach': {'days': reach_days, 'percentage': 25},
                    'act': {'days': act_days, 'percentage': 35},
                    'convert': {'days': convert_days, 'percentage': 30},
                    'engage': {'days': engage_days, 'percentage': 10}
                }
        
        prompt = f"""Generate a {duration_days}-day content calendar for {platform}.

GOAL: {goal}

PLATFORM: {platform}
Platform specs: {json.dumps(specs, indent=2)}

ICPs:
{json.dumps([{'name': icp['name'], 'psychographics': icp.get('psychographics'), 'platforms': icp.get('platforms')} for icp in icps], indent=2)}

{f"POSITIONING: {positioning.get('word')}" if positioning else ""}

RACE ALLOCATION:
{json.dumps(race_allocation, indent=2)}

REQUIREMENTS:
1. 4:1 VALUE RATIO - For every 4 educational/entertaining/inspirational posts, 1 promotional
2. Platform-specific formatting - Respect {platform} specs
3. Vary ICPs - Target different personas across posts
4. Optimal posting times - Based on ICP behaviors
5. RACE progression - Follow the phase allocation
6. Hook-first - First line/frame must grab attention
7. CTA appropriate to RACE phase

For EACH day, generate 1-3 posts (more if daily posting platform).

For EACH post provide:
{{
  "day": 1,
  "date": "2025-01-15",
  "posts": [
    {{
      "post_id": "day1_post1",
      "time": "09:00",  // Optimal posting time
      "race_phase": "reach",
      "icp_target": "ICP name",
      "content_type": "educational|entertaining|inspirational|promotional",
      "format": "text|video|carousel|image",
      
      // PLATFORM-SPECIFIC CONTENT
      "text": "Full post text within {specs['text_max']} chars",
      "hook": "First line that grabs attention",
      "body": "Main content",
      "cta": "Call to action",
      
      // METADATA
      "hashtags": ["hashtag1", "hashtag2"],  // Within {specs.get('hashtag_optimal', 5)}
      "mentions": ["@user1"],  // If relevant
      "media_description": "What image/video should show",
      "link": "URL if needed",
      
      // STRATEGY
      "objective": "What this post achieves",
      "expected_engagement": "high|medium|low",
      "why_this_time": "Why posting at this time",
      
      // VALIDATION
      "validation": {{
        "text_length": 245,
        "within_specs": true,
        "warnings": []
      }}
    }}
  ]
}}

Generate ALL {duration_days} days. Make content DIVERSE and ENGAGING.
"""
        
        response = self.gemini.generate_content(prompt)
        result = json.loads(response.text)
        
        # Validate each post
        validated_calendar = []
        total_posts = 0
        value_posts = 0
        promo_posts = 0
        
        for day_data in result.get('calendar', []):
            validated_day = day_data.copy()
            validated_posts = []
            
            for post in day_data['posts']:
                # Validate against platform specs
                validation = json.loads(self.validator._run(
                    action='validate',
                    platform=platform,
                    content={
                        'text': post['text'],
                        'hashtags': post.get('hashtags', [])
                    }
                ))
                
                post['validation'] = validation
                post['valid'] = validation['status'] != 'INVALID'
                
                validated_posts.append(post)
                total_posts += 1
                
                if post['content_type'] == 'promotional':
                    promo_posts += 1
                else:
                    value_posts += 1
            
            validated_day['posts'] = validated_posts
            validated_calendar.append(validated_day)
        
        # Calculate ratios
        value_ratio = round(value_posts / promo_posts, 2) if promo_posts > 0 else 'N/A'
        
        return json.dumps({
            'platform': platform,
            'duration_days': duration_days,
            'calendar': validated_calendar,
            'statistics': {
                'total_posts': total_posts,
                'value_posts': value_posts,
                'promotional_posts': promo_posts,
                'value_ratio': f"{value_ratio}:1",
                'meets_4_1_ratio': value_ratio >= 4.0 if promo_posts > 0 else True,
                'race_distribution': self._calculate_race_distribution(validated_calendar)
            },
            'validation_summary': {
                'all_valid': all(p['valid'] for day in validated_calendar for p in day['posts']),
                'invalid_count': sum(1 for day in validated_calendar for p in day['posts'] if not p['valid'])
            }
        })
    
    def _calculate_race_distribution(self, calendar):
        distribution = {'reach': 0, 'act': 0, 'convert': 0, 'engage': 0}
        for day in calendar:
            for post in day['posts']:
                phase = post.get('race_phase', 'reach')
                distribution[phase] = distribution.get(phase, 0) + 1
        return distribution
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
