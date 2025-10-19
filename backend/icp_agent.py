"""
Wrapper: expose `generate_icps(business_data, positioning) -> list` over LangGraph app.

Looks for:
  - backend.agents.icp.app
  - agents.icp.app
  - ICPAgent().app
"""

from typing import Any, Dict, List

_app = None
try:
    from backend.agents.icp import app as _app  # type: ignore
except Exception:
    try:
        from agents.icp import app as _app  # type: ignore
    except Exception:
        _app = None

if _app is None:
    try:
        from backend.agents.icp import ICPAgent  # type: ignore
        _app = ICPAgent().app
    except Exception:
        try:
            from agents.icp import ICPAgent  # type: ignore
            _app = ICPAgent().app
        except Exception:
            _app = None


async def generate_icps(business_data: Dict[str, Any], positioning: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Invoke the compiled LangGraph app with a best-effort state shape.
    Returns a list of ICP dicts; if the app returns a dict, look for `icps` key.
    """
    if _app is None:
        raise RuntimeError("ICP LangGraph app not found")

    candidates = [
        {"business": business_data, "positioning": positioning},
        {"input": {"business": business_data, "positioning": positioning}},
        {"business": business_data, **(positioning or {})},
    ]
    last_err = None
    for state in candidates:
        try:
            out = await _app.ainvoke(state)  # type: ignore[attr-defined]
            if isinstance(out, dict):
                if "icps" in out and isinstance(out["icps"], list):
                    return out["icps"]
                # Sometimes graphs return under 'result' or 'data'
                for k in ("result", "data"):
                    v = out.get(k)
                    if isinstance(v, dict) and isinstance(v.get("icps"), list):
                        return v["icps"]
            # Fallback: coerce to list
            return out if isinstance(out, list) else [out]
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"ICP app invocation failed: {last_err}")
