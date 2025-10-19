from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class TagExtractorTool(BaseTool):
    name = "tag_extractor"
    description = """
    Extract monitoring tags from ICP for Perplexity trend tracking.
    
    Tags should be:
    - Specific enough to find relevant trends
    - Broad enough to get results
    - Mix of: industry terms, lifestyle keywords, hashtags, events
    
    Examples:
    tag_extractor(icp={...})
    tag_extractor(action='validate', tags=[...])
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'extract',
        icp: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        count: int = 10
    ) -> str:
        
        if action == 'extract':
            if not icp:
                raise ValueError("extract requires: icp")
            
            prompt = f"""Extract {count} monitoring tags for trend tracking from this ICP profile.

ICP:
Name: {icp.get('name')}
Demographics: {json.dumps(icp.get('demographics', {}))}
Psychographics: {json.dumps(icp.get('psychographics', {}))}
Platforms: {icp.get('platforms', [])}
Interests: {json.dumps(icp.get('behaviors', {}).get('content_preferences', {}).get('topics', []))}

Tags will be used to search Perplexity daily for trends. Generate {count} tags that are:

1. SPECIFIC enough to find relevant content
2. BROAD enough to get results
3. MIX of types:
   - Industry keywords (e.g., "sustainable fashion")
   - Platform hashtags (e.g., "#productivityhacks")
   - Lifestyle terms (e.g., "remote work")
   - Event types (e.g., "tech conferences")
   - Product categories (e.g., "meal kit services")

Good examples:
- "vegan restaurants Singapore"
- "#sustainableliving"
- "AI productivity tools"
- "executive coaching"
- "fintech startups India"

Bad examples (too broad):
- "business"
- "technology"
- "food"

Return JSON:
{{
  "tags": [
    {{
      "tag": "specific tag string",
      "type": "industry|hashtag|lifestyle|event|product",
      "rationale": "Why this matches the ICP",
      "expected_frequency": "high|medium|low"
    }}
  ]
}}"""
            
            response = self.gemini.generate_content(prompt)
            result = json.loads(response.text)
            
            # Extract just the tag strings for easy use
            tag_strings = [t['tag'] for t in result['tags']]
            
            return json.dumps({
                'icp': icp.get('name'),
                'tags': tag_strings,
                'detailed_tags': result['tags'],
                'count': len(tag_strings)
            })
        
        elif action == 'validate':
            if not tags:
                raise ValueError("validate requires: tags")
            
            prompt = f"""Validate these monitoring tags for quality.

Tags: {json.dumps(tags)}

Evaluate each tag:
1. SPECIFICITY: Not too broad, not too narrow (0.0-1.0)
2. SEARCHABILITY: Will it return relevant results? (0.0-1.0)
3. RELEVANCE: Matches ICP interests? (0.0-1.0)

Return JSON:
{{
  "validated_tags": [
    {{
      "tag": "...",
      "scores": {{
        "specificity": 0.8,
        "searchability": 0.9,
        "relevance": 0.7
      }},
      "overall_score": 0.8,
      "issues": ["Problems if any"],
      "recommendation": "keep|revise|remove"
    }}
  ],
  "overall_quality": 0.0-1.0,
  "suggestions": ["Better alternatives for weak tags"]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        elif action == 'enhance':
            if not tags or not icp:
                raise ValueError("enhance requires: tags, icp")
            
            prompt = f"""Enhance these monitoring tags to be more specific and relevant.

Current Tags: {json.dumps(tags)}

ICP Context: {json.dumps(icp, indent=2)}

For each tag, suggest:
1. More specific variations
2. Related tags we should add
3. Platform-specific versions

Return JSON:
{{
  "enhanced_tags": [
    {{
      "original": "...",
      "variations": ["more specific version 1", "version 2"],
      "related": ["related tag 1", "tag 2"],
      "platform_specific": {{
        "twitter": "...",
        "linkedin": "...",
        "instagram": "..."
      }}
    }}
  ],
  "recommended_additions": ["New tags to consider"]
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
