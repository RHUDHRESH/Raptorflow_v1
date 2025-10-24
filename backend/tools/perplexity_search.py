from langchain.tools import BaseTool
from typing import Optional, List
import httpx
import os
import json
from datetime import datetime

class PerplexitySearchTool(BaseTool):
    name = "perplexity_search"
    description = """
    Deep research using Perplexity AI. Modes:
    - research: General research query (Sonar Pro model)
    - competitor: Competitor analysis (focused search)
    - trends: Latest trends in a topic (time-filtered)
    - news: Recent news about topic (last 7 days)
    
    Examples:
    perplexity_search(query='competitors of Tesla in EV market', mode='competitor')
    perplexity_search(query='sustainable fashion trends 2025', mode='trends')
    perplexity_search(query='latest AI news', mode='news', recency='day')
    """
    
    def __init__(self):
        super().__init__()
    
    def _run(
        self,
        query: str,
        mode: str = 'research',
        recency: str = 'month',  # month, week, day
        return_images: bool = False,
        return_related: bool = False,
        max_tokens: int = 1000
    ) -> str:
        
        # Customize system prompt based on mode
        system_prompts = {
            'research': 'You are a research assistant. Provide comprehensive findings with authoritative sources.',
            'competitor': 'You are a competitive analyst. Focus on market positioning, strengths, weaknesses, and unique value propositions.',
            'trends': 'You are a trend analyst. Identify emerging patterns, growing topics, and future directions.',
            'news': 'You are a news analyst. Summarize recent developments with key facts and implications.'
        }
        
        system_prompt = system_prompts.get(mode, system_prompts['research'])
        
        # Make API call
        base_url = "https://api.perplexity.ai/chat/completions"
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar-pro",
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "max_tokens": max_tokens,
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "return_citations": True,
                        "return_images": return_images,
                        "return_related_questions": return_related,
                        "search_recency_filter": recency
                    }
                )
                
                data = response.json()
                
                # Structure the response
                result = {
                    'query': query,
                    'mode': mode,
                    'findings': data['choices'][0]['message']['content'],
                    'citations': data.get('citations', []),
                    'images': data.get('images', []) if return_images else [],
                    'related_questions': data.get('related_questions', []) if return_related else [],
                    'timestamp': datetime.utcnow().isoformat(),
                    'tokens_used': data['usage']['total_tokens']
                }
                
                return json.dumps(result, indent=2)
                
        except httpx.HTTPError as e:
            return json.dumps({
                'error': True,
                'message': f'Perplexity API error: {str(e)}',
                'query': query
            })
        except Exception as e:
            return json.dumps({
                'error': True,
                'message': f'Unexpected error: {str(e)}',
                'query': query
            })
    
    async def _arun(self, *args, **kwargs):
        # Async version
        query = kwargs.get('query')
        mode = kwargs.get('mode', 'research')
        recency = kwargs.get('recency', 'month')
        return_images = kwargs.get('return_images', False)
        return_related = kwargs.get('return_related', False)
        max_tokens = kwargs.get('max_tokens', 1000)
        
        system_prompts = {
            'research': 'You are a research assistant. Provide comprehensive findings with authoritative sources.',
            'competitor': 'You are a competitive analyst. Focus on market positioning, strengths, weaknesses, and unique value propositions.',
            'trends': 'You are a trend analyst. Identify emerging patterns, growing topics, and future directions.',
            'news': 'You are a news analyst. Summarize recent developments with key facts and implications.'
        }
        
        system_prompt = system_prompts.get(mode, system_prompts['research'])
        
        base_url = "https://api.perplexity.ai/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar-pro",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": query}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "return_citations": True,
                        "return_images": return_images,
                        "return_related_questions": return_related,
                        "search_recency_filter": recency
                    }
                )
                
                data = response.json()
                
                result = {
                    'query': query,
                    'mode': mode,
                    'findings': data['choices'][0]['message']['content'],
                    'citations': data.get('citations', []),
                    'images': data.get('images', []) if return_images else [],
                    'related_questions': data.get('related_questions', []) if return_related else [],
                    'timestamp': datetime.utcnow().isoformat(),
                    'tokens_used': data['usage']['total_tokens']
                }
                
                return json.dumps(result, indent=2)
                
        except Exception as e:
            return json.dumps({
                'error': True,
                'message': f'Error: {str(e)}',
                'query': query
            })
