from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json
from datetime import datetime, timedelta

class RACEPlannerTool(BaseTool):
    name = "race_planner"
    description = """
    Build RACE calendar structure (Reach, Act, Convert, Engage).
    
    RACE phases:
    - Reach: Awareness, discovery (top of funnel)
    - Act: Engagement, consideration (middle)
    - Convert: Sales, conversion (bottom)
    - Engage: Retention, advocacy (post-purchase)
    
    Examples:
    race_planner(duration_days=30, goal='100 leads')
    race_planner(action='map_content', phase='reach', icp={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'plan',
        duration_days: int = 30,
        goal: Optional[str] = None,
        phase: Optional[str] = None,
        icp: Optional[Dict] = None,
        positioning: Optional[Dict] = None
    ) -> str:
        
        if action == 'plan':
            if not goal:
                raise ValueError("plan requires: goal")
            
            prompt = f"""Create RACE calendar structure for a {duration_days}-day campaign.

GOAL: {goal}

RACE Framework:
- REACH (Awareness): Make prospects aware you exist
- ACT (Engagement): Get them to interact and consider
- CONVERT (Sales): Turn them into customers
- ENGAGE (Retention): Keep them coming back, make them advocates

For a {duration_days}-day campaign, suggest:

1. PHASE ALLOCATION
   - How many days for each phase?
   - What percentage of content per phase?
   - Budget allocation per phase?

2. PHASE OBJECTIVES
   - Reach: Specific awareness goals
   - Act: Specific engagement goals
   - Convert: Specific conversion goals
   - Engage: Specific retention goals

3. CONTENT MIX per phase
   - Reach: Content types and ratios
   - Act: Content types and ratios
   - Convert: Content types and ratios
   - Engage: Content types and ratios

4. METRICS per phase
   - What to measure at each stage
   - Success thresholds

5. TRANSITION TRIGGERS
   - When to move someone from Reach  Act
   - When to move from Act  Convert
   - When to move from Convert  Engage

Return JSON:
{{
  "duration_days": {duration_days},
  "phase_allocation": {{
    "reach": {{"days": 8, "content_percentage": 30, "budget_percentage": 25}},
    "act": {{"days": 10, "content_percentage": 30, "budget_percentage": 30}},
    "convert": {{"days": 8, "content_percentage": 25, "budget_percentage": 35}},
    "engage": {{"days": 4, "content_percentage": 15, "budget_percentage": 10}}
  }},
  "phase_objectives": {{...}},
  "content_mix": {{...}},
  "metrics": {{...}},
  "transition_triggers": {{...}},
  "daily_structure": [
    {{
      "day": 1,
      "phase": "reach",
      "focus": "Brand awareness",
      "content_types": ["video", "carousel"],
      "platforms": ["instagram", "twitter"]
    }},
    ...
  ]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'map_content':
            if not phase or not icp:
                raise ValueError("map_content requires: phase, icp")
            
            prompt = f"""Generate content ideas for the {phase.upper()} phase of RACE.

PHASE: {phase}
ICP: {icp.get('name')}
Psychographics: {json.dumps(icp.get('psychographics', {}))}
Platforms: {icp.get('platforms', [])}

{f"POSITIONING: {positioning.get('word')}" if positioning else ""}

For the {phase} phase, suggest 10 content ideas that:
- Match the phase objective
- Resonate with this ICP
- Work on their preferred platforms
- Support the positioning (if provided)

REACH phase = Make them aware (educational, entertaining, inspirational)
ACT phase = Make them engage (interactive, valuable, conversation-starting)
CONVERT phase = Make them buy (social proof, offers, urgency)
ENGAGE phase = Keep them (community, insider content, rewards)

Return JSON:
{{
  "phase": "{phase}",
  "icp": "{icp.get('name')}",
  "content_ideas": [
    {{
      "id": 1,
      "title": "Content title/hook",
      "format": "video|carousel|text|infographic",
      "platform": "instagram|linkedin|twitter|youtube",
      "description": "What this content is about",
      "objective": "Specific goal for this piece",
      "cta": "Call-to-action",
      "estimated_engagement": "high|medium|low"
    }}
  ]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'validate':
            if not duration_days:
                raise ValueError("validate requires: duration_days with RACE allocation")
            
            # This would validate if a proposed RACE plan makes sense
            prompt = f"""Validate this RACE calendar structure.

{json.dumps({'duration_days': duration_days, 'goal': goal}, indent=2)}

Check:
1. Is phase allocation realistic?
2. Are objectives achievable?
3. Is content mix appropriate?
4. Are metrics measurable?
5. Do transition triggers make sense?

Return JSON with validation results."""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
