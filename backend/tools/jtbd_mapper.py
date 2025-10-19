from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class JTBDMapperTool(BaseTool):
    name = "jtbd_mapper"
    description = """
    Map Jobs-to-be-Done using Clayton Christensen's framework.
    
    Jobs are functional, emotional, and social.
    Format: "When [situation], I want to [motivation], so I can [outcome]"
    
    Operations:
    - map: Create JTBD map for persona
    - validate: Check JTBD quality
    - prioritize: Rank jobs by importance
    - find_gaps: Compare jobs vs product
    
    Examples:
    jtbd_mapper(persona={...})
    jtbd_mapper(action='prioritize', jobs=[...])
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'map',
        persona: Optional[Dict] = None,
        jobs: Optional[List[Dict]] = None,
        product_features: Optional[List[str]] = None
    ) -> str:
        
        if action == 'map':
            if not persona:
                raise ValueError("map requires: persona")
            
            prompt = f"""Map Jobs-to-be-Done for this persona using Clayton Christensen's framework.

PERSONA:
Name: {persona.get('name')}
Archetype: {persona.get('archetype')}
Demographics: {json.dumps(persona.get('demographics', {}))}
Psychographics: {json.dumps(persona.get('psychographics', {}))}
Goals: {json.dumps(persona.get('goals_challenges', {}).get('goals', []))}
Challenges: {json.dumps(persona.get('goals_challenges', {}).get('challenges', []))}

Jobs-to-be-Done Framework:
People don't buy products - they "hire" them to do a job.

Identify THREE types of jobs:

1. FUNCTIONAL JOBS (Practical tasks - what they're trying to accomplish)
   Examples:
   - "When I'm commuting, I want to use dead time productively, so I can learn new skills"
   - "When preparing meals, I want to minimize decision fatigue, so I can eat healthy without stress"

2. EMOTIONAL JOBS (Feelings - how they want to feel or avoid feeling)
   Examples:
   - "When facing a challenge, I want to feel confident, so I can take action without fear"
   - "When with friends, I want to avoid feeling left out, so I can maintain social status"

3. SOCIAL JOBS (Perception - how they want to be perceived)
   Examples:
   - "When posting on social media, I want to be seen as successful, so I can build my personal brand"
   - "When choosing products, I want to appear environmentally conscious, so I can align with my values publicly"

For EACH job provide:
- Job statement (When [situation], I want to [motivation], so I can [outcome])
- Success criteria (How they measure if job is done well)
- Current alternatives (How they're getting job done now - competing solutions)
- Satisfaction level (How well current alternatives work: 1-10)
- Frequency (How often this job arises: daily, weekly, monthly, occasionally)
- Importance (How important this job is: critical, high, medium, low)

Return JSON:
{{
  "functional_jobs": [
    {{
      "statement": "When...",
      "success_criteria": ["criterion 1", "criterion 2"],
      "current_alternatives": ["alternative 1", "alternative 2"],
      "satisfaction_level": 6,
      "frequency": "daily",
      "importance": "critical"
    }}
  ],
  "emotional_jobs": [...],
  "social_jobs": [...]
}}

Provide 3-5 jobs per category."""
            
            response = self.gemini.generate_content(prompt)
            result = json.loads(response.text)
            
            # Calculate priority scores
            importance_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            frequency_map = {'daily': 4, 'weekly': 3, 'monthly': 2, 'occasionally': 1}
            
            all_jobs = (
                result['functional_jobs'] + 
                result['emotional_jobs'] + 
                result['social_jobs']
            )
            
            for job in all_jobs:
                importance_score = importance_map.get(job['importance'], 2)
                frequency_score = frequency_map.get(job['frequency'], 2)
                satisfaction_gap = 10 - job['satisfaction_level']
                
                # Priority = (Importance * Frequency * Satisfaction Gap) / 100
                job['priority_score'] = round(
                    (importance_score * frequency_score * satisfaction_gap) / 100,
                    3
                )
            
            return json.dumps({
                'persona': persona.get('name'),
                'jtbd_map': result,
                'total_jobs': len(all_jobs),
                'top_priority_job': max(all_jobs, key=lambda x: x['priority_score'])
            })
        
        elif action == 'validate':
            if not jobs:
                raise ValueError("validate requires: jobs")
            
            prompt = f"""Validate these Jobs-to-be-Done for quality.

{json.dumps(jobs, indent=2)}

Check:
1. Are they in proper JTBD format? (When [situation], I want to [motivation], so I can [outcome])
2. Are they specific enough?
3. Do they avoid solution-speak? (Should describe job, not product features)
4. Are success criteria measurable?
5. Are current alternatives realistic?

Return JSON:
{{
  "is_valid": true|false,
  "quality_score": 0.0-1.0,
  "issues": [
    {{
      "job_index": 0,
      "issue": "Problem description"
    }}
  ],
  "recommendations": ["How to improve"]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'prioritize':
            if not jobs:
                raise ValueError("prioritize requires: jobs")
            
            # Recalculate priority scores if needed
            importance_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            frequency_map = {'daily': 4, 'weekly': 3, 'monthly': 2, 'occasionally': 1}
            
            for job in jobs:
                if 'priority_score' not in job:
                    importance_score = importance_map.get(job.get('importance', 'medium'), 2)
                    frequency_score = frequency_map.get(job.get('frequency', 'occasionally'), 1)
                    satisfaction_gap = 10 - job.get('satisfaction_level', 5)
                    
                    job['priority_score'] = round(
                        (importance_score * frequency_score * satisfaction_gap) / 100,
                        3
                    )
            
            # Sort by priority
            sorted_jobs = sorted(jobs, key=lambda x: x['priority_score'], reverse=True)
            
            return json.dumps({
                'prioritized_jobs': sorted_jobs,
                'top_3': sorted_jobs[:3],
                'priority_rationale': "Ranked by: (Importance  Frequency  Satisfaction Gap)"
            })
        
        elif action == 'find_gaps':
            if not jobs or not product_features:
                raise ValueError("find_gaps requires: jobs, product_features")
            
            prompt = f"""Analyze gaps between customer jobs and product features.

CUSTOMER JOBS:
{json.dumps(jobs, indent=2)}

PRODUCT FEATURES:
{json.dumps(product_features, indent=2)}

Identify:
1. Which jobs are well-served by product features?
2. Which jobs are UNDER-served (gaps)?
3. Which features don't map to any job (waste)?
4. Priority jobs to focus on

Return JSON:
{{
  "well_served_jobs": [
    {{
      "job": "...",
      "matching_features": ["feature 1", "feature 2"],
      "coverage_score": 0.8
    }}
  ],
  "under_served_jobs": [
    {{
      "job": "...",
      "gap_description": "Why this isn't served",
      "opportunity_score": 0.9
    }}
  ],
  "unused_features": ["Features that don't serve any job"],
  "recommendations": [
    {{
      "action": "build|enhance|remove",
      "target": "Job or feature",
      "rationale": "Why this matters"
    }}
  ]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
