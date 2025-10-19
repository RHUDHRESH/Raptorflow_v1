import os

ENVIRONMENT = os.getenv("ENV", "development")
"""Application environment: development or production."""

FAST_MODEL = os.getenv("FAST_MODEL", "gemini-2.0-flash-exp" if ENVIRONMENT == "development" else "gpt-4o-mini")
REASONING_MODEL = os.getenv("REASONING_MODEL", "gemini-2.0-flash-thinking-exp" if ENVIRONMENT == "development" else "gpt-4o")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004" if ENVIRONMENT == "development" else "text-embedding-3-small")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "raptorflow-adapt")

DEFAULT_TIMEOUT = float(os.getenv("DEFAULT_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

AVAILABLE_MODELS = {
    "fast": FAST_MODEL,
    "reasoning": REASONING_MODEL,
    "embedding": EMBEDDING_MODEL,
}

# Subscription Tiers
SUBSCRIPTION_TIERS = {
    "basic": {
        "price_inr": 2000,
        "max_icps": 3,
        "max_moves": 5,
        "features": ["positioning", "basic_icps", "content_calendar"],
        "trend_monitoring": False,
        "route_back_logic": False,
    },
    "pro": {
        "price_inr": 3500,
        "max_icps": 6,
        "max_moves": 15,
        "features": ["positioning", "advanced_icps", "content_calendar", "trend_monitoring", "strategy_layer"],
        "trend_monitoring": True,
        "route_back_logic": True,
    },
    "enterprise": {
        "price_inr": 5000,
        "max_icps": 9,
        "max_moves": 999,
        "features": ["positioning", "advanced_icps", "content_calendar", "trend_monitoring", "strategy_layer", "knowledge_graph"],
        "trend_monitoring": True,
        "route_back_logic": True,
        "white_label": True,
    },
}

"""Centralised configuration for AI services and environment settings."""
