from typing import List, Dict
import re
from utils.gemini_client import get_gemini_client

class AISafetyGuardrails:
    """Prevent harmful AI outputs and inputs"""
    
    # Harmful content patterns
    HARMFUL_PATTERNS = [
        r'kill\s+yourself',
        r'commit\s+suicide',
        r'self\s+harm',
        r'hack\s+into',
        r'create\s+virus',
        r'make\s+bomb',
        r'illegal\s+drugs',
        r'scam\s+people'
    ]
    
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r'ignore\s+(all\s+)?previous\s+instructions',
        r'disregard\s+(all\s+)?previous\s+instructions',
        r'forget\s+(all\s+)?previous\s+instructions',
        r'you\s+are\s+now\s+a',
        r'system\s*:\s*',
        r'<\|im_start\|>',
        r'<\|im_end\|>'
    ]
    
    @staticmethod
    def validate_input(text: str) -> bool:
        """Check input for harmful content or injection attempts"""
        
        # Check for harmful content
        for pattern in AISafetyGuardrails.HARMFUL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError(f"Input contains harmful content")
        
        # Check for prompt injection
        for pattern in AISafetyGuardrails.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError(f"Input contains potential prompt injection")
        
        return True
    
    @staticmethod
    def validate_output(text: str, context: str = None) -> bool:
        """Validate AI output for safety"""
        
        # Use Gemini's safety filters
        gemini = get_gemini_client()
        
        safety_prompt = f"""Analyze this text for harmful content:

Text: {text}

Check for:
1. Harmful instructions
2. Illegal advice
3. Discriminatory content
4. Privacy violations
5. Misinformation

Return JSON:
{{
  "is_safe": true/false,
  "issues": ["list of issues if any"],
  "severity": "none|low|medium|high"
}}"""
        
        response = gemini.generate_content(safety_prompt)
        result = json.loads(response.text)
        
        if not result['is_safe'] or result['severity'] in ['high', 'medium']:
            raise ValueError(f"Output failed safety check: {result['issues']}")
        
        return True
    
    @staticmethod
    def sanitize_output(text: str) -> str:
        """Sanitize AI output"""
        
        # Remove any potential code execution
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        # Remove SQL injection attempts
        text = re.sub(r'DROP\s+TABLE', '', text, flags=re.IGNORECASE)
        text = re.sub(r'DELETE\s+FROM', '', text, flags=re.IGNORECASE)
        
        return text

# Middleware to apply AI safety
async def ai_safety_middleware(request: Request, call_next):
    """Apply AI safety checks to all AI interactions"""
    
    # For POST requests with JSON body
    if request.method == "POST":
        body = await request.json()
        
        # Check all text fields
        for key, value in body.items():
            if isinstance(value, str):
                try:
                    AISafetyGuardrails.validate_input(value)
                except ValueError as e:
                    return JSONResponse(
                        status_code=400,
                        content={"error": str(e), "field": key}
                    )
    
    response = await call_next(request)
    return response
