import os
import google.generativeai as genai

_genai_client = None

def get_gemini_client():
    """Initialise and cache the Gemini client."""
    global _genai_client
    if _genai_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        genai.configure(api_key=api_key)
        _genai_client = genai.GenerativeModel("gemini-2.0-flash")
    return _genai_client
