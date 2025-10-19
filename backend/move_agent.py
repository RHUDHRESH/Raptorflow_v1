"""
Wrapper: expose `generate_move_calendar(business_data, icps, goal, platform, duration_days) -> dict`
over LangGraph app.

Looks for:
  - backend.agents.moves.app OR backend.agents.content.app
  - agents.moves.app OR agents.content.app
  - ContentAgent().app (or MovesAgent().app)
"""

from typing import Any, Dict, List

_app = None

# Try moves app first
try:
    from backend.agents.moves import app as _app  # type: ignore
except Exception:
    try:
        from agents.moves import app as _app  # type: ignore
    except Exception:
        _app = None

# Fall back to content app (your repo uses content.py for moves)
if _app is None:
    try:
        from backend.agents.content import app as _app  # type: ignore
    except Exception:
        try:
            from agents.content import app as _app  # type: ignore
        except Exception:
            _app = None

# Try instantiating an agent class if no module-level app is exported
if _app is None:
    for _mod_name, _cls_name in [
        ("backend.agents.content", "ContentAgent"),
        ("agents.content", "ContentAgent"),
        ("backend.agents.moves", "MovesAgent"),
        ("agents.moves", "MovesAgent"),
    ]:
        try:
            _mod = __import__(_mod_name, fromlist=[_cls_name])
            _cls = getattr(_mod, _cls_name)
            _app = _cls().app
            break
        except Exception:
            continue


async def generate_move_calendar(
    business_data: Dict[str, Any],
    icps: List[Dict[str, Any]],
    goal: str,
    platform: str,
    duration_days: int,
) -> Dict[str, Any]:
    """
    Invoke the compiled LangGraph app with a best-effort state shape.
    Returns a dict; if not a dict, it is wrapped under {'calendar': <value>}.
    """
    if _app is None:
        raise RuntimeError("Move/Content LangGraph app not found")

    candidates = [
        {
            "business": business_data,
            "icps": icps,
            "goal": goal,
            "platform": platform,
            "duration_days": duration_days,
        },
        {"input": {
            "business": business_data,
            "icps": icps,
            "goal": goal,
            "platform": platform,
            "duration_days": duration_days,
        }},
        {
            "business": business_data,
            "icps": icps,
            "request": {"goal": goal, "platform": platform, "duration_days": duration_days},
        },
    ]
    last_err = None
    for state in candidates:
        try:
            out = await _app.ainvoke(state)  # type: ignore[attr-defined]
            if isinstance(out, dict):
                return out
            return {"calendar": out}
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Move calendar app invocation failed: {last_err}")
