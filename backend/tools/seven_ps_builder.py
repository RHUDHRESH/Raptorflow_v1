from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class SevenPsBuilderTool(BaseTool):
    name = "seven_ps_builder"
    description = """
    Build marketing mix using 7Ps framework:
    1. Product - What you sell
    2. Price - Pricing strategy
    3. Place - Distribution channels
    4. Promotion - Marketing tactics
    5. People - Team & customer service
    6. Process - Customer journey
    7. Physical Evidence - Tangible proof
    
    Examples:
    seven_ps_builder(business_data={...}, positioning={...}, icps=[...])
    seven_ps_builder(action='validate', seven_ps={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'build',
        business_data: Optional[Dict] = None,
        positioning: Optional[Dict] = None,
        icps: Optional[List[Dict]] = None,
        seven_ps: Optional[Dict] = None
    ) -> str:
        
        if action == 'build':
            if not business_data or not positioning:
                raise ValueError("build requires: business_data, positioning")
            
            prompt = f"""Build comprehensive 7Ps marketing mix for this business.

BUSINESS:
{json.dumps(business_data, indent=2)}

POSITIONING:
Word to Own: {positioning.get('word')}
Rationale: {positioning.get('rationale')}
Sacrifices: {json.dumps(positioning.get('sacrifices', []))}

ICPs:
{json.dumps([{{'name': icp.get('name'), 'demographics': icp.get('demographics'), 'psychographics': icp.get('psychographics')}} for icp in (icps or [])], indent=2)}

Create detailed 7Ps strategy:

1. PRODUCT
   - Core offering description
   - Key features that reinforce positioning
   - Product differentiation (vs competitors)
   - Quality level
   - Packaging/presentation
   - Service elements
   - Brand elements

2. PRICE
   - Pricing strategy (premium, value, penetration, skimming)
   - Price points (specific numbers)
   - Psychological pricing tactics
   - Discounts/promotions strategy
   - Payment terms
   - Price positioning vs competitors
   - Rationale (based on "wound size" - how bad is their pain?)

3. PLACE
   - Distribution channels (primary and secondary)
   - Geographic coverage
   - Online vs offline split
   - Partnerships/intermediaries
   - Logistics approach
   - Inventory strategy

4. PROMOTION
   - Key marketing channels (ranked)
   - Message strategy (what we say)
   - Content approach
   - Advertising tactics
   - PR strategy
   - Sales promotions
   - Budget allocation by channel

5. PEOPLE
   - Team requirements (roles needed)
   - Customer service approach
   - Training needs
   - Culture alignment with positioning
   - Customer-facing processes
   - Internal communication

6. PROCESS
   - Customer journey map (awareness  purchase  retention)
   - Touchpoint strategy
   - Automation opportunities
   - Quality control
   - Efficiency measures
   - Feedback loops

7. PHYSICAL EVIDENCE
   - Tangible proof points
   - Website/digital presence
   - Office/store environment
   - Packaging and materials
   - Documentation
   - Brand assets
   - Social proof (reviews, testimonials, case studies)

For each P, explain HOW it reinforces the positioning "{positioning.get('word')}".

Return as JSON with these exact keys."""
            
            response = self.gemini.generate_content(prompt)
            result = json.loads(response.text)
            
            return json.dumps({
                'seven_ps': result,
                'positioning': positioning.get('word'),
                'created_for': business_data.get('name')
            })
        
        elif action == 'validate':
            if not seven_ps:
                raise ValueError("validate requires: seven_ps")
            
            prompt = f"""Validate this 7Ps marketing mix for completeness and strategic alignment.

{json.dumps(seven_ps, indent=2)}

Evaluate:
1. COMPLETENESS: Are all 7Ps thoroughly addressed? (0.0-1.0 per P)
2. ALIGNMENT: Do all Ps reinforce the same positioning? (0.0-1.0)
3. FEASIBILITY: Can this actually be executed? (0.0-1.0)
4. DIFFERENTIATION: Does this stand out from competitors? (0.0-1.0)

Return JSON:
{{
  "completeness_scores": {{
    "product": 0.9,
    "price": 0.8,
    "place": 0.7,
    "promotion": 0.9,
    "people": 0.6,
    "process": 0.8,
    "physical_evidence": 0.7
  }},
  "overall_completeness": 0.8,
  "alignment_score": 0.9,
  "feasibility_score": 0.7,
  "differentiation_score": 0.8,
  "strengths": ["Strong points"],
  "weaknesses": ["Weak areas"],
  "gaps": ["Missing elements"],
  "recommendations": ["Specific improvements"]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'optimize':
            if not seven_ps or not positioning:
                raise ValueError("optimize requires: seven_ps, positioning")
            
            prompt = f"""Optimize this 7Ps mix to better reinforce the positioning.

POSITIONING: {positioning.get('word')}

CURRENT 7PS:
{json.dumps(seven_ps, indent=2)}

For each P, suggest:
1. What to keep (already strong)
2. What to change (not aligned with positioning)
3. What to add (missing opportunities)

Focus on making the entire mix SING with the positioning.

Return JSON:
{{
  "optimizations": {{
    "product": {{
      "keep": ["..."],
      "change": ["..."],
      "add": ["..."]
    }},
    ...for all 7Ps
  }},
  "priority_changes": ["Top 5 most important changes"],
  "expected_impact": "How these changes strengthen positioning"
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
