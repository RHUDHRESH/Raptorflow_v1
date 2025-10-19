from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
from tools.platform_validator import PlatformValidatorTool
import json

class MultiChannelAdapterTool(BaseTool):
    name = "multi_channel_adapter"
    description = """
    Adapt content for multiple platforms while keeping core message.
    
    Takes one "master" message and creates platform-specific versions:
    - Twitter: Punchy, thread-ready
    - LinkedIn: Professional, thought leadership
    - Instagram: Visual-first, story-driven
    - YouTube: Long-form, educational
    
    Examples:
    multi_channel_adapter(message='...', platforms=['twitter', 'linkedin', 'instagram'])
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
        self.validator = PlatformValidatorTool()
    
    def _run(
        self,
        message: str,
        platforms: List[str],
        tone: str = 'professional',
        include_media_brief: bool = False
    ) -> str:
        
        platform_characteristics = {
            'twitter': {
                'style': 'Punchy, concise, thread-worthy',
                'length': 'Short (100-250 chars per tweet)',
                'tone': 'Conversational, direct',
                'format': 'Tweet or thread',
                'hashtags': '1-2 max',
                'hook': 'First 100 chars crucial'
            },
            'linkedin': {
                'style': 'Professional thought leadership',
                'length': 'Medium (150-300 chars optimal)',
                'tone': 'Authoritative but accessible',
                'format': 'Standalone post or article',
                'hashtags': '3-5 relevant',
                'hook': 'Strong opening statement'
            },
            'instagram': {
                'style': 'Visual storytelling, emotive',
                'length': 'Medium (138 chars optimal)',
                'tone': 'Personal, authentic',
                'format': 'Caption for image/reel',
                'hashtags': '5-9 strategic',
                'hook': 'Visual + first line'
            },
            'youtube': {
                'style': 'Educational, detailed',
                'length': 'Long-form (script 1000+ words)',
                'tone': 'Explanatory, engaging',
                'format': 'Video script with timestamps',
                'hashtags': 'N/A (tags instead)',
                'hook': 'First 15 seconds critical'
            },
            'tiktok': {
                'style': 'Entertaining, trend-aware',
                'length': 'Very short (21-34s video)',
                'tone': 'Casual, fun',
                'format': 'Video script',
                'hashtags': '3-5 trending',
                'hook': 'First 3 seconds hook'
            }
        }
        
        prompt = f"""Adapt this core message for {len(platforms)} different platforms.

CORE MESSAGE:
{message}

TONE: {tone}

PLATFORMS: {', '.join(platforms)}

For EACH platform, create a version that:
1. Keeps the core message intact
2. Adapts to platform norms and best practices
3. Optimizes for that platform's algorithm
4. Respects character/time limits
5. Uses platform-appropriate language

Platform Characteristics:
{json.dumps({p: platform_characteristics[p] for p in platforms if p in platform_characteristics}, indent=2)}

Return JSON:
{{
  "core_message": "{message}",
  "adaptations": [
    {{
      "platform": "twitter",
      "version": {{
        "format": "thread|single",
        "content": "Tweet text or array of tweets",
        "hook": "First line",
        "hashtags": ["#tag1", "#tag2"],
        "character_count": 245,
        "thread_structure": ["Tweet 1", "Tweet 2", "Tweet 3"],  // If thread
        "image_suggestion": "What visual to pair with this"
      }}
    }},
    {{
      "platform": "linkedin",
      "version": {{
        "content": "Full post text",
        "hook": "Opening line",
        "body": "Main content",
        "cta": "Call to action",
        "hashtags": ["#Hashtag1", "#Hashtag2"],
        "character_count": 287,
        "post_type": "text|article|poll",
        "image_suggestion": "Professional visual"
      }}
    }},
    {{
      "platform": "instagram",
      "version": {{
        "caption": "Full caption text",
        "hook": "First line",
        "story_telling_elements": ["Beginning", "Middle", "End"],
        "hashtags": ["#hashtag1", "#hashtag2"],
        "character_count": 156,
        "format": "feed|reel|story",
        "visual_brief": "What the image/video should show",
        "emoji_usage": ["", ""]
      }}
    }},
    {{
      "platform": "youtube",
      "version": {{
        "title": "Video title (60 chars)",
        "description": "Video description (first 250 chars)",
        "script_outline": ["Intro", "Point 1", "Point 2", "Conclusion"],
        "timestamps": {{
          "00:00": "Intro",
          "00:30": "Main content",
          "03:45": "Conclusion"
        }},
        "tags": ["tag1", "tag2"],
        "thumbnail_concept": "What thumbnail shows"
      }}
    }}
  ],
  "consistency_check": "How all versions maintain core message"
}}

Make each adaptation NATIVE to the platform while keeping message consistent."""
        
        response = self.gemini.generate_content(prompt)
        result = json.loads(response.text)
        
        # Validate each adaptation
        for adaptation in result['adaptations']:
            platform = adaptation['platform']
            version = adaptation['version']
            
            # Get validation for text content
            content_to_validate = None
            if platform == 'twitter':
                if version.get('format') == 'thread':
                    content_to_validate = {'text': version['thread_structure'][0]}
                else:
                    content_to_validate = {'text': version['content']}
            elif platform in ['linkedin', 'instagram']:
                content_to_validate = {
                    'text': version.get('content') or version.get('caption'),
                    'hashtags': version.get('hashtags', [])
                }
            
            if content_to_validate:
                validation = json.loads(self.validator._run(
                    action='validate',
                    platform=platform,
                    content=content_to_validate
                ))
                adaptation['validation'] = validation
        
        return json.dumps(result, indent=2)
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
