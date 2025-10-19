from fastapi import HTTPException, Request
from pydantic import BaseModel, validator, Field
from typing import Optional
import re

class BusinessIntakeGuardrails(BaseModel):
    """Strict validation for business intake"""
    name: str = Field(..., min_length=2, max_length=100)
    industry: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    goals: str = Field(..., min_length=10, max_length=500)
    
    @validator('name')
    def validate_name(cls, v):
        """Prevent injection attacks and profanity"""
        if not re.match(r'^[a-zA-Z0-9\s\-&.]+$', v):
            raise ValueError('Business name contains invalid characters')
        
        # Check for profanity (basic example)
        profanity_list = ['badword1', 'badword2']  # Add comprehensive list
        if any(word in v.lower() for word in profanity_list):
            raise ValueError('Business name contains inappropriate content')
        
        return v
    
    @validator('description', 'goals')
    def validate_text_content(cls, v):
        """Prevent prompt injection and harmful content"""
        # Check for prompt injection patterns
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'system\s*:',
            r'<\s*script',
            r'DROP\s+TABLE',
            r'SELECT\s+\*\s+FROM'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Text contains potentially harmful content')
        
        return v
    
    @validator('industry')
    def validate_industry(cls, v):
        """Validate against known industries"""
        valid_industries = [
            'SaaS', 'E-commerce', 'Healthcare', 'Education', 'Finance',
            'Real Estate', 'Manufacturing', 'Retail', 'Technology',
            'Consulting', 'Marketing', 'Hospitality', 'Agriculture'
        ]
        
        # Allow custom but log for review
        if v not in valid_industries:
            # Log for manual review
            import logging
            logging.warning(f"Custom industry submitted: {v}")
        
        return v

class MetricsInputGuardrails(BaseModel):
    """Validate performance metrics"""
    impressions: int = Field(..., ge=0, le=10_000_000)
    engagements: int = Field(..., ge=0, le=1_000_000)
    clicks: int = Field(..., ge=0, le=500_000)
    conversions: int = Field(..., ge=0, le=100_000)
    revenue: float = Field(..., ge=0, le=10_000_000)
    
    @validator('engagements')
    def engagement_must_be_less_than_impressions(cls, v, values):
        """Engagements can't exceed impressions"""
        if 'impressions' in values and v > values['impressions']:
            raise ValueError('Engagements cannot exceed impressions')
        return v
    
    @validator('clicks')
    def clicks_must_be_less_than_engagements(cls, v, values):
        """Clicks can't exceed engagements"""
        if 'engagements' in values and v > values['engagements']:
            raise ValueError('Clicks cannot exceed engagements')
        return v
    
    @validator('conversions')
    def conversions_must_be_less_than_clicks(cls, v, values):
        """Conversions can't exceed clicks"""
        if 'clicks' in values and v > values['clicks']:
            raise ValueError('Conversions cannot exceed clicks')
        return v
