from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
from utils.supabase_client import get_supabase_client
import json

class RouteBackLogicTool(BaseTool):
    name = "route_back_logic"
    description = """
    Determine if campaign failure requires route-back to earlier stage.
    
    Decision tree:
    - Low clarity (<0.5)  Route back to Positioning
    - Wrong audience (<0.5)  Route back to ICP
    - Poor execution (<0.5)  Route back to Strategy/Tactics
    - All good but no results  Market timing issue
    
    Examples:
    route_back_logic(performance_data={...}, campaign_data={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
        self.supabase = get_supabase_client()
    
    def _run(
        self,
        business_id: str,
        performance_data: Dict,
        campaign_data: Dict
    ) -> str:
        
        prompt = f"""Analyze campaign performance and determine if route-back is needed.

CAMPAIGN:
{json.dumps(campaign_data, indent=2)}

PERFORMANCE:
{json.dumps(performance_data, indent=2)}

ROUTE-BACK DECISION FRAMEWORK:

Evaluate three dimensions (score each 0.0-1.0):

1. CLARITY (Do people understand what we are?)
   Signals:
   - Low engagement despite reach  Unclear positioning
   - High bounce rate  Message doesn't resonate
   - Confused comments/questions  Unclear value prop
   
   If clarity < 0.5  Route back to POSITIONING

2. AUDIENCE FIT (Are we talking to the right people?)
   Signals:
   - Engagement from wrong demographics  Wrong ICP
   - Low conversion despite engagement  Audience not ready to buy
   - Mismatched psychographics  Values don't align
   
   If audience_fit < 0.5  Route back to ICP

3. EXECUTION (Is our content/tactics working?)
   Signals:
   - Right audience but no engagement  Bad content
   - Good content but wrong platform  Channel mismatch
   - Inconsistent posting  Execution failure
   
   If execution < 0.5  Route back to STRATEGY/TACTICS

4. MARKET TIMING (Is this the right time?)
   Signals:
   - Everything looks good but no results  Market not ready
   - External factors (economy, season, trends)
   
   If all scores > 0.5 but results poor  MARKET TIMING

Return JSON:
{{
  "scores": {{
    "clarity": 0.7,
    "audience_fit": 0.4,
    "execution": 0.8,
    "overall": 0.63
  }},
  "route_back_needed": true,
  "route_back_to": "icp",  // positioning|icp|strategy|tactics|null
  "diagnosis": "Detailed explanation of what's wrong",
  "evidence": [
    "Signal 1 that led to this conclusion",
    "Signal 2",
    "Signal 3"
  ],
  "recommended_fixes": [
    {{
      "stage": "icp",
      "action": "Redefine target segment to focus on X demographic",
      "rationale": "Current ICP showing low conversion",
      "expected_impact": "high|medium|low"
    }}
  ],
  "should_continue_campaign": false,
  "next_steps": [
    "Step 1: Pause current campaign",
    "Step 2: Re-run ICP analysis with performance data",
    "Step 3: Generate new personas based on who actually engaged",
    "Step 4: Restart campaign with refined ICPs"
  ]
}}"""
        
        response = self.gemini.generate_content(prompt)
        result = json.loads(response.text)
        
        # Log route-back decision to database
        if result['route_back_needed']:
            self.supabase.table('route_back_logs').insert({
                'business_id': business_id,
                'from_stage': 'campaign_execution',
                'to_stage': result['route_back_to'],
                'reason': result['diagnosis'],
                'decision_data': {
                    'scores': result['scores'],
                    'evidence': result['evidence'],
                    'recommended_fixes': result['recommended_fixes']
                },
                'resolved': False
            }).execute()
        
        return json.dumps(result, indent=2)
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
