"""
Compatibility shim for legacy imports.

Projects that previously imported:
    from backend.middleware.ai_safety_middleware import ...
should continue to work. This module re-exports symbols from ai_safety.py.
"""
try:
    from .ai_safety import *  # re-export everything from the canonical module
except Exception as _e:
    # Fallback no-op so imports don't crash during partial setups
    pass
