from langchain.tools import BaseTool
from typing import Dict, Any
from utils.gemini_client import get_gemini_client
from utils.supabase_client import get_supabase_client
import json

class SOSTACAnalyzerTool(BaseTool):
    name = "sostac_analyzer"
    description = """
    Analyze business using SOSTAC framework:
    - Situation: Where are we now?
    - Objectives: Where do we want to be?
    - Strategy: How do we get there?
    - Tactics: What specific actions?
    - Action: What's the plan?
    - Control: How do we measure?
    
    Examples:
    sostac_analyzer(business_id='uuid', business_data={...})
    sostac_analyzer(action='get', business_id='uuid')
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
        self.supabase = get_supabase_client()
    
    def _run(
        self,
        action: str = 'analyze',
        business_id: str = None,
        business_data: Dict = None
    ) -> str:
        
        if action == 'analyze':
            if not business_data:
                raise ValueError("analyze requires: business_data")
            
            prompt = f"""Perform comprehensive SOSTAC analysis for this business:

Business Name: {business_data.get('name')}
Industry: {business_data.get('industry')}
Location: {business_data.get('location')}
Description: {business_data.get('description')}
Goals: {business_data.get('goals')}

Provide detailed analysis for each SOSTAC element:

## SITUATION (Where are we now?)
Analyze:
- Current market position
- Competitive landscape assessment
- SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
- Internal capabilities
- External market forces
- Customer perception (if inferable)

## OBJECTIVES (Where do we want to be?)
Define:
- SMART objectives (Specific, Measurable, Achievable, Relevant, Time-bound)
- Revenue targets
- Market share goals
- Brand awareness metrics
- Customer acquisition targets
- Timeline for achievement

## STRATEGY (How do we get there?)
Outline:
- High-level strategic approach
- Target market segments
- Positioning strategy
- Competitive strategy (differentiation, cost leadership, niche)
- Growth strategy (market penetration, development, diversification)
- Value proposition

## TACTICS (What specific actions?)
Detail:
- Marketing mix (7Ps):
  * Product: What we sell
  * Price: Pricing strategy
  * Place: Distribution channels
  * Promotion: Marketing tactics
  * People: Team and customer service
  * Process: Customer journey
  * Physical Evidence: Tangible proof points
- Channel strategy
- Campaign types
- Content approach

## ACTION (What's the plan?)
Specify:
- Priority actions (first 30/60/90 days)
- Resource allocation
- Budget requirements
- Responsibilities and ownership
- Implementation timeline
- Quick wins vs. long-term initiatives

## CONTROL (How do we measure?)
Define:
- Key Performance Indicators (KPIs)
- Monitoring frequency
- Reporting structure
- Adjustment triggers (when to change course)
- Success metrics
- Feedback loops

Return as JSON with these exact keys: situation, objectives, strategy, tactics, action, control
Each value should be an object with detailed subsections."""

            response = self.gemini.generate_content(prompt)
            sostac = json.loads(response.text)
            
            # Save to database
            result = self.supabase.table('sostac_analyses').insert({
                'business_id': business_id,
                **sostac
            }).execute()
            
            return json.dumps({
                'success': True,
                'sostac_id': result.data[0]['id'],
                'analysis': sostac
            })
        
        elif action == 'get':
            if not business_id:
                raise ValueError("get requires: business_id")
            
            result = self.supabase.table('sostac_analyses')\
                .select('*')\
                .eq('business_id', business_id)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return json.dumps(result.data[0])
            else:
                return json.dumps({'error': 'No SOSTAC analysis found'})
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
