from typing import Any, Dict, List
import json

class DataQualityGuardrails:
    """Ensure data quality across the system"""
    
    @staticmethod
    def validate_positioning_option(option: Dict) -> bool:
        """Validate positioning option completeness"""
        
        required_fields = [
            'word', 'rationale', 'big_idea', 'purple_cow',
            'differentiation_score', 'sacrifices', 'visual_hammers'
        ]
        
        for field in required_fields:
            if field not in option:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate scores are in range
        if not 0 <= option['differentiation_score'] <= 1:
            raise ValueError("differentiation_score must be between 0 and 1")
        
        # Validate word length
        if len(option['word']) > 50:
            raise ValueError("Positioning word too long (max 50 chars)")
        
        # Validate sacrifices exist
        if len(option['sacrifices']) < 3:
            raise ValueError("Must have at least 3 sacrifices (Law of Sacrifice)")
        
        return True
    
    @staticmethod
    def validate_icp(icp: Dict) -> bool:
        """Validate ICP completeness"""
        
        required_sections = [
            'name', 'demographics', 'psychographics',
            'jtbd', 'value_proposition', 'platforms'
        ]
        
        for section in required_sections:
            if section not in icp:
                raise ValueError(f"Missing ICP section: {section}")
        
        # Validate demographics
        demo = icp['demographics']
        required_demo = ['age', 'income', 'location', 'occupation']
        for field in required_demo:
            if field not in demo:
                raise ValueError(f"Missing demographic field: {field}")
        
        # Validate JTBD structure
        jtbd = icp['jtbd']
        if not all(key in jtbd for key in ['functional_jobs', 'emotional_jobs', 'social_jobs']):
            raise ValueError("JTBD must include all three job types")
        
        return True
    
    @staticmethod
    def validate_calendar(calendar: Dict) -> bool:
        """Validate content calendar quality"""
        
        # Check 4:1 value ratio
        stats = calendar.get('statistics', {})
        value_posts = stats.get('value_posts', 0)
        promo_posts = stats.get('promotional_posts', 0)
        
        if promo_posts > 0:
            ratio = value_posts / promo_posts
            if ratio < 4:
                raise ValueError(f"Value ratio too low: {ratio:.1f}:1 (should be 4:1)")
        
        # Validate all posts
        for day in calendar.get('calendar', []):
            for post in day.get('posts', []):
                if not post.get('text'):
                    raise ValueError(f"Post on day {day['day']} missing text")
                
                if not post.get('valid', True):
                    raise ValueError(f"Post on day {day['day']} failed platform validation")
        
        return True

# Middleware to enforce data quality
async def data_quality_middleware(request: Request, call_next):
    """Validate data quality before saving"""
    
    response = await call_next(request)
    
    # For POST/PUT endpoints that return structured data
    if request.method in ["POST", "PUT"] and response.status_code == 200:
        try:
            body = response.json()
            
            # Validate based on endpoint
            if '/positioning' in request.url.path and 'options' in body:
                for option in body['options']:
                    DataQualityGuardrails.validate_positioning_option(option)
            
            elif '/icps' in request.url.path and 'icps' in body:
                for icp in body['icps']:
                    DataQualityGuardrails.validate_icp(icp)
            
            elif '/moves' in request.url.path and 'calendar' in body:
                DataQualityGuardrails.validate_calendar(body['calendar'])
        
        except Exception as e:
            # Log validation error but don't block (allow manual review)
            import logging
        logging.error(f"Data quality validation failed: {e}")
    
    return response
