from langchain.tools import BaseTool
import json

class PlatformValidatorTool(BaseTool):
    name = "platform_validator"
    description = """
    Validate content against platform specifications.
    
    Checks:
    - Text length limits
    - Video duration limits
    - Image specs
    - Hashtag limits
    - Link restrictions
    
    Examples:
    platform_validator(platform='twitter', content={...})
    platform_validator(action='get_specs', platform='instagram')
    """
    
    def __init__(self):
        super().__init__()
        self.specs = {
            'twitter': {
                'text_max': 280,
                'text_optimal': 100,  # Tweets < 100 chars get more engagement
                'video_max_duration': '2:20',
                'video_max_size_mb': 512,
                'image_max_count': 4,
                'image_formats': ['jpg', 'png', 'gif', 'webp'],
                'hashtag_max': 2,  # More than 2 decreases engagement
                'hashtag_optimal': 1,
                'link_count': 1,
                'threads_max_tweets': 25
            },
            'linkedin': {
                'text_max': 3000,
                'text_optimal': 150,  # Posts 150-200 chars perform best
                'video_max_duration': '15:00',
                'video_max_size_mb': 5000,
                'image_max_count': 9,
                'image_formats': ['jpg', 'png', 'gif'],
                'hashtag_max': 30,
                'hashtag_optimal': 3,
                'link_count': 1,
                'pdf_max_size_mb': 100,
                'carousel_max_slides': 10
            },
            'instagram': {
                'caption_max': 2200,
                'caption_optimal': 138,  # Captions ~138 chars perform best
                'reel_max_duration': '90s',
                'reel_optimal_duration': '7-15s',
                'video_max_duration': '60:00',
                'image_formats': ['jpg', 'png'],
                'hashtag_max': 30,
                'hashtag_optimal': 9,
                'mention_max': 20,
                'carousel_max_slides': 10,
                'story_duration': '15s'
            },
            'youtube': {
                'title_max': 100,
                'title_optimal': 60,
                'description_max': 5000,
                'description_optimal': 250,
                'video_max_duration': '12:00:00',
                'shorts_max_duration': '60s',
                'tags_max': 500,  # characters
                'tags_optimal_count': 15,
                'thumbnail_size': '1280x720',
                'thumbnail_max_mb': 2
            },
            'tiktok': {
                'caption_max': 2200,
                'video_max_duration': '10:00',
                'video_optimal_duration': '21-34s',
                'hashtag_max': 30,
                'hashtag_optimal': 5,
                'video_formats': ['mp4', 'mov']
            }
        }
    
    def _run(
        self,
        action: str = 'validate',
        platform: str = None,
        content: Optional[Dict] = None
    ) -> str:
        
        if not platform or platform not in self.specs:
            return json.dumps({
                'error': f"Platform '{platform}' not supported",
                'supported_platforms': list(self.specs.keys())
            })
        
        if action == 'get_specs':
            return json.dumps({
                'platform': platform,
                'specs': self.specs[platform]
            })
        
        elif action == 'validate':
            if not content:
                raise ValueError("validate requires: content")
            
            spec = self.specs[platform]
            violations = []
            warnings = []
            
            # Check text length
            if 'text' in content:
                text_len = len(content['text'])
                if text_len > spec['text_max']:
                    violations.append({
                        'field': 'text',
                        'issue': 'TOO_LONG',
                        'current': text_len,
                        'max': spec['text_max'],
                        'message': f"Text is {text_len} chars, max is {spec['text_max']}"
                    })
                elif text_len > spec.get('text_optimal', spec['text_max']):
                    warnings.append({
                        'field': 'text',
                        'issue': 'LONGER_THAN_OPTIMAL',
                        'current': text_len,
                        'optimal': spec['text_optimal'],
                        'message': f"Text is {text_len} chars, optimal is {spec['text_optimal']}"
                    })
            
            # Check video duration
            if 'video_duration' in content:
                duration = content['video_duration']
                max_duration = spec.get('video_max_duration', '99:99')
                
                if self._duration_to_seconds(duration) > self._duration_to_seconds(max_duration):
                    violations.append({
                        'field': 'video_duration',
                        'issue': 'TOO_LONG',
                        'current': duration,
                        'max': max_duration,
                        'message': f"Video is {duration}, max is {max_duration}"
                    })
            
            # Check hashtag count
            if 'hashtags' in content:
                hashtag_count = len(content['hashtags'])
                if hashtag_count > spec.get('hashtag_max', 999):
                    violations.append({
                        'field': 'hashtags',
                        'issue': 'TOO_MANY',
                        'current': hashtag_count,
                        'max': spec['hashtag_max'],
                        'message': f"Using {hashtag_count} hashtags, max is {spec['hashtag_max']}"
                    })
                elif hashtag_count > spec.get('hashtag_optimal', 999):
                    warnings.append({
                        'field': 'hashtags',
                        'issue': 'MORE_THAN_OPTIMAL',
                        'current': hashtag_count,
                        'optimal': spec['hashtag_optimal'],
                        'message': f"Using {hashtag_count} hashtags, optimal is {spec['hashtag_optimal']}"
                    })
            
            # Check image count
            if 'image_count' in content:
                image_count = content['image_count']
                if image_count > spec.get('image_max_count', 999):
                    violations.append({
                        'field': 'image_count',
                        'issue': 'TOO_MANY',
                        'current': image_count,
                        'max': spec['image_max_count'],
                        'message': f"Using {image_count} images, max is {spec['image_max_count']}"
                    })
            
            # Determine overall status
            if violations:
                status = 'INVALID'
            elif warnings:
                status = 'WARNING'
            else:
                status = 'VALID'
            
            return json.dumps({
                'platform': platform,
                'status': status,
                'violations': violations,
                'warnings': warnings,
                'can_publish': len(violations) == 0,
                'recommendations': self._get_recommendations(violations, warnings)
            })
        
        elif action == 'suggest_fix':
            if not content:
                raise ValueError("suggest_fix requires: content")
            
            # First validate
            validation = json.loads(self._run(action='validate', platform=platform, content=content))
            
            if validation['status'] == 'VALID':
                return json.dumps({
                    'message': 'Content is valid, no fixes needed',
                    'content': content
                })
            
            fixed_content = content.copy()
            fixes_applied = []
            
            # Fix text length violations
            for violation in validation['violations']:
                if violation['field'] == 'text' and violation['issue'] == 'TOO_LONG':
                    original_text = fixed_content['text']
                    max_len = violation['max']
                    
                    # Try to truncate at sentence boundary
                    truncated = original_text[:max_len]
                    last_period = truncated.rfind('.')
                    if last_period > max_len * 0.7:  # If we can keep 70%+, truncate there
                        fixed_content['text'] = truncated[:last_period + 1]
                    else:
                        fixed_content['text'] = truncated[:max_len - 3] + '...'
                    
                    fixes_applied.append(f"Truncated text from {len(original_text)} to {len(fixed_content['text'])} chars")
                
                elif violation['field'] == 'hashtags' and violation['issue'] == 'TOO_MANY':
                    original_count = len(fixed_content['hashtags'])
                    max_hashtags = violation['max']
                    fixed_content['hashtags'] = fixed_content['hashtags'][:max_hashtags]
                    fixes_applied.append(f"Reduced hashtags from {original_count} to {max_hashtags}")
            
            return json.dumps({
                'original_content': content,
                'fixed_content': fixed_content,
                'fixes_applied': fixes_applied,
                'validation': self._run(action='validate', platform=platform, content=fixed_content)
            })
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _duration_to_seconds(self, duration_str: str) -> int:
        """Convert duration string like '2:20' or '90s' to seconds"""
        if 's' in duration_str:
            return int(duration_str.replace('s', ''))
        
        parts = duration_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    
    def _get_recommendations(self, violations, warnings):
        recommendations = []
        
        for v in violations:
            if v['issue'] == 'TOO_LONG':
                recommendations.append(f"Shorten {v['field']} to {v['max']} or less")
            elif v['issue'] == 'TOO_MANY':
                recommendations.append(f"Reduce {v['field']} to {v['max']} or less")
        
        for w in warnings:
            if w['issue'] == 'LONGER_THAN_OPTIMAL':
                recommendations.append(f"Consider shortening {w['field']} to {w['optimal']} for better engagement")
        
        return recommendations
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
