from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class AssetFactoryTool(BaseTool):
    name = "asset_factory"
    description = """
    Generate asset briefs for visual content creation.
    
    Creates detailed briefs for:
    - Images (hero, carousel, infographic)
    - Videos (scripts, storyboards)
    - Graphics (quotes, stats)
    
    Note: Generates BRIEFS, not actual assets (use Canva API for that)
    
    Examples:
    asset_factory(post={...}, format='carousel')
    asset_factory(action='video_script', duration=30, message='...')
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'generate_brief',
        post: Optional[Dict] = None,
        format: Optional[str] = None,
        duration: Optional[int] = None,
        message: Optional[str] = None
    ) -> str:
        
        if action == 'generate_brief':
            if not post:
                raise ValueError("generate_brief requires: post")
            
            format = post.get('format', 'image')
            
            if format == 'carousel':
                return self._carousel_brief(post)
            elif format == 'video':
                return self._video_brief(post, duration)
            elif format == 'image':
                return self._image_brief(post)
            elif format == 'infographic':
                return self._infographic_brief(post)
            else:
                return json.dumps({'error': f'Unsupported format: {format}'})
        
        elif action == 'video_script':
            if not duration or not message:
                raise ValueError("video_script requires: duration, message")
            
            prompt = f"""Write a {duration}-second video script.

MESSAGE: {message}

Structure for {duration}s:
- 0-3s: Hook (grab attention immediately)
- 3-{duration-5}s: Body (deliver value)
- {duration-5}-{duration}s: CTA (clear next step)

Format:
{{
  "script": [
    {{
      "timestamp": "0-3s",
      "visual": "What's on screen",
      "text_on_screen": "Text overlay",
      "voiceover": "What to say",
      "notes": "Direction notes"
    }}
  ],
  "total_words": 75,
  "speaking_pace": "slow|medium|fast"
}}"""
            
            response = self.gemini.generate_content(prompt)
            return response.text
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _carousel_brief(self, post):
        prompt = f"""Create a carousel brief for this post.

POST CONTENT:
{json.dumps(post, indent=2)}

Generate 6-10 carousel slides. For each slide:
1. Headline (big, bold text)
2. Body text (supporting detail)
3. Visual elements (icons, colors, imagery)
4. Design notes

Return JSON:
{{
  "carousel_title": "Overall theme",
  "color_scheme": ["#hex1", "#hex2", "#hex3"],
  "font_style": "modern|classic|playful",
  "slides": [
    {{
      "slide_number": 1,
      "type": "cover|content|cta",
      "headline": "Big text",
      "body": "Supporting text",
      "visual_elements": ["icon: rocket", "background: gradient"],
      "design_notes": "Keep minimal, focus on headline"
    }}
  ],
  "canva_template_suggestion": "Template name or URL"
}}"""
        
        response = self.gemini.generate_content(prompt)
        return response.text
    
    def _video_brief(self, post, duration=None):
        duration = duration or 30
        
        prompt = f"""Create a video brief for this post.

POST: {json.dumps(post, indent=2)}
DURATION: {duration} seconds

Provide:
1. Concept overview
2. Scene-by-scene breakdown
3. Visual style
4. Music/sound suggestions
5. B-roll needs
6. Text overlays

Return JSON:
{{
  "concept": "Overall video idea",
  "duration": {duration},
  "visual_style": "minimalist|energetic|cinematic|casual",
  "scenes": [
    {{
      "timestamp": "0-5s",
      "shot": "Close-up of...",
      "action": "What happens",
      "text_overlay": "Text on screen",
      "voiceover": "Spoken words",
      "b_roll": ["supporting footage 1", "footage 2"]
    }}
  ],
  "music": {{
    "mood": "upbeat|calm|intense",
    "bpm": 120,
    "suggestions": ["track name 1", "track 2"]
  }},
  "equipment_needed": ["iPhone", "tripod", "ring light"]
}}"""
        
        response = self.gemini.generate_content(prompt)
        return response.text
    
    def _image_brief(self, post):
        prompt = f"""Create an image brief for this post.

POST: {json.dumps(post, indent=2)}

Provide:
1. Image concept
2. Composition
3. Color palette
4. Text overlay (if any)
5. Stock photo suggestions

Return JSON:
{{
  "concept": "What the image shows",
  "composition": "Center-focused|rule-of-thirds|minimal",
  "color_palette": ["#hex1", "#hex2"],
  "dimensions": "1080x1080 (Instagram square)",
  "text_overlay": {{
    "text": "Words on image",
    "placement": "top|center|bottom",
    "font": "bold sans-serif",
    "size": "large"
  }},
  "stock_photo_keywords": ["keyword1", "keyword2"],
  "style": "professional|casual|artistic"
}}"""
        
        response = self.gemini.generate_content(prompt)
        return response.text
    
    def _infographic_brief(self, post):
        prompt = f"""Create an infographic brief for this post.

POST: {json.dumps(post, indent=2)}

Provide:
1. Data visualization strategy
2. Layout structure
3. Icon/chart types
4. Color coding
5. Text hierarchy

Return JSON:
{{
  "title": "Infographic title",
  "layout": "vertical|horizontal|circular",
  "sections": [
    {{
      "section_number": 1,
      "type": "stat|chart|process|comparison",
      "content": "What this section shows",
      "visual": "pie-chart|bar-graph|icon-grid",
      "data_points": ["Point 1: 75%", "Point 2: 25%"]
    }}
  ],
  "color_scheme": ["#primary", "#secondary", "#accent"],
  "icon_style": "line|filled|flat",
  "dimensions": "1080x1920 (Instagram story)"
}}"""
        
        response = self.gemini.generate_content(prompt)
        return response.text
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
