from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class PersonaGeneratorTool(BaseTool):
    name = "persona_generator"
    description = """
    Generate detailed customer personas with demographics, psychographics, behaviors.
    
    Operations:
    - generate: Create N personas for a positioning
    - enrich: Add more details to existing persona
    - validate: Check persona quality
    - compare: Compare multiple personas
    
    Examples:
    persona_generator(positioning={...}, count=3)
    persona_generator(action='enrich', persona={...}, focus='psychographics')
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'generate',
        positioning: Optional[Dict] = None,
        segment_hypothesis: Optional[str] = None,
        count: int = 3,
        persona: Optional[Dict] = None,
        focus: Optional[str] = None
    ) -> str:
        
        if action == 'generate':
            if not positioning:
                raise ValueError("generate requires: positioning")
            
            prompt = f"""Create {count} distinct customer personas for this positioning.

POSITIONING:
Word to Own: {positioning.get('word')}
Rationale: {positioning.get('rationale')}

{f"SEGMENT HYPOTHESIS: {segment_hypothesis}" if segment_hypothesis else ""}

Create {count} DISTINCT personas. Make them different ages, backgrounds, motivations.

For EACH persona provide:

1. NAME & ARCHETYPE
   - First name (realistic)
   - Age (specific, not range)
   - One-sentence archetype (e.g., "The Busy Professional")

2. DEMOGRAPHICS
   - Age: Specific age (e.g., 34, not 30-35)
   - Gender: Male/Female/Non-binary
   - Income: Specific (e.g., "$85,000/year")
   - Location: City, State/Country
   - Occupation: Specific job title
   - Education: Highest degree
   - Family: Relationship status, kids
   - Housing: Own/rent, type

3. PSYCHOGRAPHICS (This is crucial)
   - Core Values: 4 deep values they hold (e.g., "authenticity", "achievement", "family")
   - Fears: 4 specific fears/pain points (e.g., "fear of wasting time", "fear of being judged")
   - Desires: 4 aspirations (e.g., "wants to be seen as successful", "craves simplicity")
   - Decision Triggers: 3 things that make them buy (e.g., "social proof", "limited time", "expert recommendation")
   - Personality Traits: 5 adjectives (e.g., "ambitious, impatient, analytical, social, skeptical")

4. BEHAVIORS
   - Daily Routine: Typical day breakdown
   - Media Consumption: What they read/watch/listen to
   - Social Media Usage: 
     * Platform 1: Name, usage pattern, content preferences
     * Platform 2: Name, usage pattern, content preferences
     * Platform 3: Name, usage pattern, content preferences
   - Shopping Behavior: How they research and buy
   - Brand Loyalties: 3-5 brands they love and why
   - Content Preferences:
     * Formats: Video, text, audio, images (ranked)
     * Tone: Casual, professional, inspirational, etc
     * Topics: 5 topics they engage with

5. GOALS & CHALLENGES
   - Primary Goal: What they're trying to achieve (big picture)
   - Secondary Goals: 2-3 supporting goals
   - Current Challenges: 3-4 obstacles they face
   - How positioning helps: Specific connection to "{positioning.word}"

6. QUOTE
   - A characteristic thing they would say (reveals personality)

Return as JSON array of personas. Make each persona VIVID and REALISTIC.
{{
  "personas": [
    {{
      "name": "...",
      "age": 34,
      "archetype": "...",
      "demographics": {{}},
      "psychographics": {{}},
      "behaviors": {{}},
      "goals_challenges": {{}},
      "quote": "..."
    }}
  ]
}}"""
            
            response = self.gemini.generate_content(prompt)
            result = json.loads(response.text)
            
            return json.dumps({
                'positioning': positioning.get('word'),
                'personas': result['personas'],
                'count': len(result['personas'])
            })
        
        elif action == 'enrich':
            if not persona:
                raise ValueError("enrich requires: persona")
            
            prompt = f"""Enrich this persona with more detail.

EXISTING PERSONA:
{json.dumps(persona, indent=2)}

{f"FOCUS ON: {focus}" if focus else "Add more depth to all sections"}

Add:
- More specific details
- Concrete examples
- Real product/brand preferences
- Actual platforms they use
- Specific content they engage with
- Nuanced psychological insights

Return the COMPLETE enriched persona as JSON."""

            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'validate':
            if not persona:
                raise ValueError("validate requires: persona")
            
            prompt = f"""Validate this persona's quality and realism.

{json.dumps(persona, indent=2)}

Evaluate:
1. SPECIFICITY: Are details specific or generic? (0.0-1.0)
2. REALISM: Does this feel like a real person? (0.0-1.0)
3. DISTINCTIVENESS: Is this different from generic personas? (0.0-1.0)
4. ACTIONABILITY: Can marketers use this? (0.0-1.0)
5. COMPLETENESS: Are all sections filled out? (0.0-1.0)

Return JSON:
{{
  "scores": {{...}},
  "overall_score": 0.0-1.0,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "recommendation": "approve|revise|reject",
  "missing_elements": ["..."]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'compare':
            if not positioning or 'personas' not in positioning:
                raise ValueError("compare requires: positioning with personas array")
            
            personas = positioning['personas']
            
            prompt = f"""Compare these {len(personas)} personas for distinctiveness.

{json.dumps(personas, indent=2)}

Analyze:
1. How different are they from each other?
2. Do they cover different segments?
3. Are any too similar?
4. What's the range of diversity (age, income, psychographics)?

Return JSON:
{{
  "distinctiveness_score": 0.0-1.0,
  "diversity_analysis": "...",
  "overlaps": ["Persona 1 and 2 are too similar because..."],
  "gaps": ["Missing segments like..."],
  "recommendation": "These personas are distinct enough|Need more diversity"
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
