"""
Wrapper: expose `analyze_positioning(business_data) -> dict` over LangGraph app.

Looks for:
  - backend.agents.positioning.app  (preferred)
  - agents.positioning.app
  - PositioningAgent().app
"""

from typing import Any, Dict

# Resolve compiled app
_app = None
try:
    from backend.agents.positioning import app as _app  # type: ignore
except Exception:
    try:
        from agents.positioning import app as _app  # type: ignore
    except Exception:
        _app = None

if _app is None:
    try:
        from backend.agents.positioning import PositioningAgent  # type: ignore
        _app = PositioningAgent().app
    except Exception:
        try:
            from agents.positioning import PositioningAgent  # type: ignore
            _app = PositioningAgent().app
        except Exception:
            _app = None


async def analyze_positioning(business_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke the compiled LangGraph app with a best-effort state shape.
    Returns whatever the graph returns (preferably a dict with 'options').
    """
    if _app is None:
        raise RuntimeError("Positioning LangGraph app not found")

    # Try a few common state shapes used in StateGraph designs
    candidates = [
        {"business": business_data},
        {"input": {"business": business_data}},
        business_data,
    ]
    last_err = None
    for state in candidates:
        try:
            result = await _app.ainvoke(state)  # type: ignore[attr-defined]
            # Prefer dict; if not, coerce minimally
            if isinstance(result, dict):
                return result
            return {"result": result}
        except Exception as e:  # keep trying other shapes
            last_err = e
            continue
    # If all shapes failed, raise the last error for the API layer to handle
    raise RuntimeError(f"Positioning app invocation failed: {last_err}")
