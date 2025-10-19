from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class SacrificeCalculatorTool(BaseTool):
    name = "sacrifice_calculator"
    description = """
    Calculate required sacrifices for positioning (Law of Sacrifice - Ries & Trout).
    
    The Law of Sacrifice states you must sacrifice:
    1. Product line - Narrow focus wins
    2. Target market - Can't be for everyone
    3. Constant change - Consistency beats flexibility
    
    Examples:
    sacrifice_calculator(positioning={...}, business_data={...})
    sacrifice_calculator(action='validate', sacrifices=[...], business_data={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'calculate',
        positioning: Optional[Dict] = None,
        business_data: Optional[Dict] = None,
        sacrifices: Optional[List[Dict]] = None
    ) -> str:
        
        if action == 'calculate':
            if not positioning or not business_data:
                raise ValueError("calculate requires: positioning, business_data")
            
            prompt = f"""Based on the Law of Sacrifice (Ries & Trout), determine what this business must give up to own this position.

POSITIONING:
Word to Own: {positioning.get('word', positioning.get('positioning'))}
Rationale: {positioning.get('rationale', '')}

BUSINESS:
Name: {business_data.get('name')}
Industry: {business_data.get('industry')}
Description: {business_data.get('description')}

The Law of Sacrifice requires giving up:
1. PRODUCT LINE - Narrow your offering to strengthen position
2. TARGET MARKET - Exclude segments that don't align
3. CONSTANT CHANGE - Commit to consistency over trends

For EACH category, provide 2-3 SPECIFIC sacrifices this business must make.
Be concrete - say WHAT to stop doing, not general advice.

Return JSON:
{{
  "sacrifices": [
    {{
      "category": "product_line|target_market|consistency",
      "sacrifice": "Specific thing to stop doing or not offer",
      "rationale": "Why this sacrifice strengthens the position",
      "difficulty": "low|medium|high",
      "impact": "How much this helps positioning (0.0-1.0)"
    }}
  ],
  "summary": "Overall sacrifice strategy in 2-3 sentences"
}}"""
            
            response = self.gemini.generate_content(prompt)
            result = json.loads(response.text)
            
            # Calculate total sacrifice score
            total_impact = sum(s['impact'] for s in result['sacrifices'])
            avg_impact = total_impact / len(result['sacrifices']) if result['sacrifices'] else 0
            
            return json.dumps({
                'positioning': positioning.get('word'),
                'sacrifices': result['sacrifices'],
                'summary': result['summary'],
                'sacrifice_score': round(avg_impact, 3),
                'difficulty_distribution': {
                    'low': len([s for s in result['sacrifices'] if s['difficulty'] == 'low']),
                    'medium': len([s for s in result['sacrifices'] if s['difficulty'] == 'medium']),
                    'high': len([s for s in result['sacrifices'] if s['difficulty'] == 'high'])
                }
            })
        
        elif action == 'validate':
            if not sacrifices or not business_data:
                raise ValueError("validate requires: sacrifices, business_data")
            
            prompt = f"""Validate if these sacrifices are sufficient and appropriate:

Business: {business_data.get('name')} in {business_data.get('industry')}

Proposed Sacrifices:
{json.dumps(sacrifices, indent=2)}

Evaluate:
1. Are these sacrifices specific enough?
2. Do they cover all three Law of Sacrifice categories?
3. Will they meaningfully strengthen positioning?
4. Are any sacrifices too extreme or unnecessary?

Return JSON:
{{
  "is_valid": true|false,
  "completeness_score": 0.0-1.0,
  "issues": ["List any problems"],
  "recommendations": ["Suggested improvements"],
  "overall_assessment": "Brief assessment"
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'compare':
            # Compare sacrifice requirements across multiple positioning options
            if not positioning or not business_data:
                raise ValueError("compare requires: positioning (list), business_data")
            
            results = []
            for pos_option in positioning:
                sacrifice_analysis = json.loads(self._run(
                    action='calculate',
                    positioning=pos_option,
                    business_data=business_data
                ))
                results.append({
                    'positioning': pos_option.get('word'),
                    'sacrifice_score': sacrifice_analysis['sacrifice_score'],
                    'sacrifices': sacrifice_analysis['sacrifices'],
                    'difficulty': sacrifice_analysis['difficulty_distribution']
                })
            
            return json.dumps({
                'options_analyzed': len(results),
                'results': results,
                'easiest_option': min(results, key=lambda x: len([s for s in x['sacrifices'] if s['difficulty'] == 'high']))['positioning'],
                'most_focused_option': max(results, key=lambda x: x['sacrifice_score'])['positioning']
            })
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
