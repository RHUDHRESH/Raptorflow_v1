from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class VisualHammerTool(BaseTool):
    name = "visual_hammer"
    description = """
    Generate visual hammer concepts (Ries - consistent visual that reinforces positioning).
    
    Visual hammers are:
    - Colors (Tiffany blue, Coca-Cola red)
    - Shapes (Nike swoosh, Apple apple)
    - Mascots (Geico gecko)
    - Packaging (Absolut bottle)
    - Symbols (Shell shell, Target target)
    
    Examples:
    visual_hammer(positioning={...}, action='generate')
    visual_hammer(action='validate', hammer_concept={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'generate',
        positioning: Optional[Dict] = None,
        business_data: Optional[Dict] = None,
        hammer_concept: Optional[Dict] = None
    ) -> str:
        
        if action == 'generate':
            if not positioning:
                raise ValueError("generate requires: positioning")
            
            prompt = f"""Generate 5 visual hammer concepts for this positioning.

POSITIONING:
Word: {positioning.get('word')}
Rationale: {positioning.get('rationale')}
Big Idea: {positioning.get('big_idea', 'N/A')}

BUSINESS:
Name: {business_data.get('name', 'N/A')}
Industry: {business_data.get('industry', 'N/A')}

A visual hammer is a consistent visual element that reinforces the verbal positioning.

Famous examples:
- Tiffany: Robin egg blue box (luxury, exclusivity)
- Marlboro: Cowboy imagery (rugged, masculine)
- Absolut: Distinctive bottle shape (premium, artistic)
- Target: Red bullseye (fun, accessible)
- Apple: Bitten apple (innovation, simplicity)

Generate 5 distinct visual hammer concepts. For each:
1. Type (color, shape, symbol, mascot, packaging, typography)
2. Description (what it looks like)
3. How it reinforces the positioning
4. Implementation (where it appears)
5. Memorability score (0.0-1.0)
6. Feasibility (easy, medium, hard)

Return JSON:
{{
  "hammers": [
    {{
      "type": "color|shape|symbol|mascot|packaging|typography",
      "name": "Short descriptive name",
      "description": "Detailed visual description",
      "positioning_link": "How it reinforces '{positioning.word}'",
      "implementation": "Where it appears (logo, packaging, ads, etc)",
      "memorability": 0.8,
      "feasibility": "easy|medium|hard",
      "examples": ["Similar concepts from other brands"]
    }}
  ]
}}"""
            
            response = self.gemini.generate_content(prompt)
            result = json.loads(response.text)
            
            # Sort by memorability
            result['hammers'].sort(key=lambda x: x['memorability'], reverse=True)
            
            return json.dumps({
                'positioning': positioning.get('word'),
                'hammers': result['hammers'],
                'recommended': result['hammers'][0],  # Highest memorability
                'count': len(result['hammers'])
            })
        
        elif action == 'validate':
            if not hammer_concept:
                raise ValueError("validate requires: hammer_concept")
            
            prompt = f"""Validate this visual hammer concept:

{json.dumps(hammer_concept, indent=2)}

Evaluate:
1. CONSISTENCY: Can it be used consistently across all touchpoints?
2. MEMORABILITY: Is it distinctive and memorable?
3. SCALABILITY: Does it work at different sizes?
4. RELEVANCE: Does it reinforce the positioning?
5. OWNABLE: Can the brand own it exclusively?
6. TIMELESS: Will it age well?

Return JSON:
{{
  "scores": {{
    "consistency": 0.0-1.0,
    "memorability": 0.0-1.0,
    "scalability": 0.0-1.0,
    "relevance": 0.0-1.0,
    "ownable": 0.0-1.0,
    "timeless": 0.0-1.0
  }},
  "overall_score": 0.0-1.0,
  "strengths": ["List strengths"],
  "weaknesses": ["List weaknesses"],
  "recommendation": "approve|revise|reject",
  "improvement_suggestions": ["If revise, how to improve"]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'compare':
            if not positioning:
                raise ValueError("compare requires: positioning with multiple hammer concepts")
            
            hammers = positioning.get('hammers', [])
            if len(hammers) < 2:
                raise ValueError("compare requires at least 2 hammer concepts")
            
            comparisons = []
            for hammer in hammers:
                validation = json.loads(self._run(
                    action='validate',
                    hammer_concept=hammer
                ))
                comparisons.append({
                    'hammer': hammer,
                    'validation': validation
                })
            
            # Sort by overall score
            comparisons.sort(key=lambda x: x['validation']['overall_score'], reverse=True)
            
            return json.dumps({
                'comparisons': comparisons,
                'winner': comparisons[0]['hammer'],
                'winner_score': comparisons[0]['validation']['overall_score']
            })
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
