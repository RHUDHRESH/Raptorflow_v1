from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
from utils.embeddings import generate_embedding
import numpy as np
import json

class RelevanceScorerTool(BaseTool):
    name = "relevance_scorer"
    description = """
    Score trend relevance to ICP using fast model (Gemini Flash).
    
    Scores 0.0-1.0 based on:
    - Topic alignment with ICP interests
    - Value alignment with ICP psychographics
    - Platform/format fit
    - Timeliness
    
    Examples:
    relevance_scorer(trend={...}, icp={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        trend: Dict,
        icp: Dict
    ) -> str:
        
        # Use both semantic similarity and AI scoring
        trend_text = f"{trend.get('title', '')} {trend.get('description', '')}"
        icp_text = f"{icp.get('name')} {json.dumps(icp.get('psychographics', {}))} {json.dumps(icp.get('behaviors', {}))}"
        
        # Semantic similarity via embeddings
        trend_embedding = generate_embedding(trend_text)
        icp_embedding = generate_embedding(icp_text)
        semantic_score = self._cosine_similarity(trend_embedding, icp_embedding)
        
        # AI-based contextual scoring
        prompt = f"""Score the relevance of this trend to this ICP (0.0-1.0).

TREND:
{json.dumps(trend, indent=2)}

ICP:
Name: {icp.get('name')}
Demographics: {json.dumps(icp.get('demographics', {}))}
Psychographics: {json.dumps(icp.get('psychographics', {}))}
Interests: {icp.get('behaviors', {}).get('content_preferences', {}).get('topics', [])}
Platforms: {icp.get('platforms', [])}

Evaluate:
1. TOPIC ALIGNMENT (0.0-1.0): Does this trend match ICP interests?
2. VALUE ALIGNMENT (0.0-1.0): Does it align with ICP values/beliefs?
3. PLATFORM FIT (0.0-1.0): Is it on platforms they use?
4. TIMELINESS (0.0-1.0): Is this trend current and rising?
5. ACTIONABILITY (0.0-1.0): Can we create content around this?

Return JSON:
{{
  "scores": {{
    "topic_alignment": 0.8,
    "value_alignment": 0.7,
    "platform_fit": 0.9,
    "timeliness": 0.6,
    "actionability": 0.8
  }},
  "overall_relevance": 0.76,  // Weighted average
  "rationale": "Why this score",
  "content_angle": "How we could leverage this trend",
  "recommendation": "use|consider|skip"
}}"""
        
        response = self.gemini.generate_content(prompt)
        result = json.loads(response.text)
        
        # Combine semantic and AI scores (70% AI, 30% semantic)
        combined_score = (result['overall_relevance'] * 0.7) + (semantic_score * 0.3)
        
        return json.dumps({
            'trend': trend.get('title', 'Unknown'),
            'icp': icp.get('name'),
            'semantic_score': round(semantic_score, 3),
            'ai_score': result['overall_relevance'],
            'combined_score': round(combined_score, 3),
            'detailed_scores': result['scores'],
            'rationale': result['rationale'],
            'content_angle': result['content_angle'],
            'recommendation': result['recommendation'],
            'should_use': combined_score > 0.7
        })
    
    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
