"""
Compatibility shim (CamelCase filename) for legacy imports.

Projects that previously imported:
    from backend.middleware.AISafetyGuardrails import ...
should continue to work. This module re-exports symbols from ai_safety.py.
"""
try:
    from .ai_safety import *  # re-export everything from the canonical module
except Exception as _e:
    pass
