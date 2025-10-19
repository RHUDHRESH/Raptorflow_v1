from langchain.tools import BaseTool
from typing import List, Dict
from utils.gemini_client import get_gemini_client
from tools.perplexity_search import PerplexitySearchTool
from tools.evidence_db import EvidenceDBTool
from utils.supabase_client import get_supabase_client
import json

class CompetitorLadderTool(BaseTool):
    name = "competitor_ladder"
    description = """
    Build competitive positioning ladder. Shows what word/concept each competitor owns.
    
    Operations:
    - build: Research competitors and extract positioning
    - add_competitor: Manually add competitor to ladder
    - get_ladder: Retrieve ladder for business
    - analyze_gap: Find unowned positioning spaces
    
    Examples:
    competitor_ladder(action='build', business_id='uuid', industry='food delivery')
    competitor_ladder(action='analyze_gap', business_id='uuid')
    """
    
    def __init__(self):
        super().__init__()
        self.perplexity = PerplexitySearchTool()
        self.evidence = EvidenceDBTool()
        self.supabase = get_supabase_client()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str,
        business_id: str,
        industry: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        competitor_name: Optional[str] = None,
        word_owned: Optional[str] = None
    ) -> str:
        
        if action == 'build':
            if not industry:
                raise ValueError("build requires: industry")
            
            # Step 1: Use Perplexity to find top competitors
            search_query = f"Top 10 competitors in {industry} market. For each, what is their main brand positioning and the single word they own in customers' minds?"
            
            search_results = self.perplexity._run(
                query=search_query,
                mode='competitor',
                recency='month'
            )
            
            search_data = json.loads(search_results)
            
            # Step 2: Use Gemini to extract structured data
            extraction_prompt = f"""Extract competitor positioning from this research:

{search_data['findings']}

For each competitor, determine:
1. Company name
2. The single word or short phrase they "own" in customers' minds
3. Position strength (0.0-1.0 based on how strongly they own it)
4. Evidence (quote from research)

Return JSON:
{{
  "competitors": [
    {{
      "competitor": "Company Name",
      "word_owned": "speed|quality|innovation|etc",
      "position_strength": 0.8,
      "evidence": "Quote from research"
    }}
  ]
}}"""
            
            response = self.gemini.generate_content(extraction_prompt)
            result = json.loads(response.text)
            
            # Step 3: Save to database
            saved_competitors = []
            for comp in result['competitors']:
                # Save to competitor_ladder table
                db_entry = self.supabase.table('competitor_ladder').insert({
                    'business_id': business_id,
                    'competitor_name': comp['competitor'],
                    'word_owned': comp['word_owned'],
                    'position_strength': comp['position_strength'],
                    'evidence': {
                        'quote': comp['evidence'],
                        'citations': search_data['citations']
                    }
                }).execute()
                
                # Also add to evidence graph
                node_id = json.loads(self.evidence._run(
                    action='create_node',
                    business_id=business_id,
                    node_type='competitor',
                    content=f"{comp['competitor']} owns '{comp['word_owned']}'",
                    metadata=comp,
                    confidence_score=comp['position_strength'],
                    source='perplexity_research'
                ))['node_id']
                
                saved_competitors.append({
                    **comp,
                    'db_id': db_entry.data[0]['id'],
                    'evidence_node_id': node_id
                })
            
            return json.dumps({
                'success': True,
                'competitors': saved_competitors,
                'count': len(saved_competitors),
                'research_citations': search_data['citations']
            })
        
        elif action == 'add_competitor':
            if not competitor_name or not word_owned:
                raise ValueError("add_competitor requires: competitor_name, word_owned")
            
            result = self.supabase.table('competitor_ladder').insert({
                'business_id': business_id,
                'competitor_name': competitor_name,
                'word_owned': word_owned,
                'position_strength': 0.5,  # Default
                'evidence': {'manual': True}
            }).execute()
            
            return json.dumps({
                'success': True,
                'competitor': result.data[0]
            })
        
        elif action == 'get_ladder':
            result = self.supabase.table('competitor_ladder')\
                .select('*')\
                .eq('business_id', business_id)\
                .order('position_strength', desc=True)\
                .execute()
            
            return json.dumps({
                'ladder': result.data,
                'count': len(result.data)
            })
        
        elif action == 'analyze_gap':
            # Get all competitors
            ladder_data = json.loads(self._run(action='get_ladder', business_id=business_id))
            competitors = ladder_data['ladder']
            
            # Extract all owned words
            owned_words = [c['word_owned'] for c in competitors]
            
            # Use Gemini to find gaps
            gap_prompt = f"""These positioning words are already owned by competitors in this market:
{', '.join(owned_words)}

Suggest 5 positioning words/concepts that are:
1. NOT owned by these competitors
2. Defensible and meaningful
3. Relevant to modern customers

Return JSON:
{{
  "gap_opportunities": [
    {{
      "word": "suggested positioning word",
      "rationale": "why this is unowned and valuable",
      "market_fit": "which customer segment would value this"
    }}
  ]
}}"""
            
            response = self.gemini.generate_content(gap_prompt)
            gaps = json.loads(response.text)
            
            return json.dumps({
                'owned_words': owned_words,
                'gap_opportunities': gaps['gap_opportunities']
            })
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
