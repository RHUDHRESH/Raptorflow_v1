from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class NorthStarCalculatorTool(BaseTool):
    name = "north_star_calculator"
    description = """
    Calculate North Star metric - the ONE metric that captures long-term value.
    
    Good North Star metrics:
    - Airbnb: Nights Booked
    - Spotify: Time Spent Listening
    - WhatsApp: Messages Sent
    - Slack: Messages Sent by Teams
    
    Bad metrics:
    - Page views (vanity)
    - Sign-ups (doesn't mean value delivered)
    - Revenue (lagging, not leading)
    
    Examples:
    north_star_calculator(business_data={...}, objectives={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'calculate',
        business_data: Optional[Dict] = None,
        objectives: Optional[Dict] = None,
        proposed_metric: Optional[str] = None
    ) -> str:
        
        if action == 'calculate':
            if not business_data or not objectives:
                raise ValueError("calculate requires: business_data, objectives")
            
            prompt = f"""Determine the North Star metric for this business.

BUSINESS:
{json.dumps(business_data, indent=2)}

OBJECTIVES:
{json.dumps(objectives, indent=2)}

The North Star metric must:
1. Express VALUE delivered to customers (not vanity)
2. LEAD to revenue (predicts business success)
3. Be ACTIONABLE (team can move it)
4. Be UNDERSTANDABLE (everyone gets it)

Examples of great North Star metrics:
- Airbnb: "Nights Booked" (value = accommodation, leads to revenue)
- Spotify: "Time Spent Listening" (value = music enjoyment, leads to retention)
- Facebook: "Daily Active Users" (value = connection, leads to ad revenue)
- Slack: "Messages Sent by Teams" (value = communication, leads to paid seats)

Suggest 3 potential North Star metrics, then pick the best.

Return JSON:
{{
  "candidates": [
    {{
      "metric": "Metric name",
      "definition": "Exactly what we measure",
      "rationale": "Why this captures customer value",
      "pros": ["Advantage 1", "Advantage 2"],
      "cons": ["Limitation 1"],
      "value_connection": "How it shows value delivered",
      "revenue_connection": "How it predicts revenue",
      "actionability": "How team can move it",
      "score": 0.0-1.0
    }}
  ],
  "recommended": {{
    "metric": "Best option",
    "why": "Reasoning",
    "measurement_frequency": "daily|weekly|monthly",
    "target_setting": "How to set targets",
    "sub_metrics": ["Supporting metrics to track"]
  }}
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'validate':
            if not proposed_metric:
                raise ValueError("validate requires: proposed_metric")
            
            prompt = f"""Validate this North Star metric.

Proposed Metric: {proposed_metric}

Check against criteria:
1. Does it express customer value? (not vanity)
2. Does it lead to revenue?
3. Is it actionable?
4. Is it understandable?
5. Is it measurable?
6. Does it avoid gaming? (can't be easily manipulated)

Return JSON:
{{
  "is_valid": true|false,
  "scores": {{
    "customer_value": 0.0-1.0,
    "revenue_leading": 0.0-1.0,
    "actionability": 0.0-1.0,
    "understandability": 0.0-1.0,
    "measurability": 0.0-1.0,
    "gaming_resistance": 0.0-1.0
  }},
  "overall_score": 0.0-1.0,
  "strengths": ["What's good"],
  "weaknesses": ["What's problematic"],
  "recommendation": "approve|revise|reject",
  "alternative_suggestions": ["If reject/revise, better options"]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
