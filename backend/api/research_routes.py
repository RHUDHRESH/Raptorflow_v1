"""
Deep Research Agent API Routes

FastAPI endpoints for the comprehensive research system.
Integrates with LangGraph for multi-agent orchestration.
"""

import logging
import uuid
import asyncio
from typing import Optional, Dict, Any
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from ..research.workflow import DeepResearchGraph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])

# Global research graph instance (initialize in startup)
_research_graph: Optional[DeepResearchGraph] = None


class ResearchRequest(BaseModel):
    """Request model for research queries"""
    query: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = None
    max_sources: int = 100
    max_depth: int = 3
    focus_areas: Optional[list] = None
    query_type: str = "hybrid"  # breadth_first, depth_first, hybrid


class ResearchResponse(BaseModel):
    """Response model for research requests"""
    thread_id: str
    status: str
    message: str


def initialize_research_graph(
    perplexity_api_key: str,
    exa_api_key: str,
    google_api_key: str,
    google_search_engine_id: str
):
    """
    Initialize the research graph (call on startup).

    Args:
        perplexity_api_key: Perplexity API key
        exa_api_key: Exa.ai API key
        google_api_key: Google API key
        google_search_engine_id: Google Custom Search engine ID
    """
    global _research_graph
    _research_graph = DeepResearchGraph(
        perplexity_api_key=perplexity_api_key,
        exa_api_key=exa_api_key,
        google_api_key=google_api_key,
        google_search_engine_id=google_search_engine_id
    )
    logger.info("Research graph initialized")


def get_research_graph() -> DeepResearchGraph:
    """Get or initialize research graph"""
    global _research_graph
    if _research_graph is None:
        raise RuntimeError("Research graph not initialized. Call initialize_research_graph() on startup.")
    return _research_graph


@router.post("/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
) -> ResearchResponse:
    """
    Start a new research task (async, runs in background).

    Args:
        request: Research query and parameters
        background_tasks: FastAPI background task manager

    Returns:
        Research session ID and status
    """
    thread_id = request.thread_id or str(uuid.uuid4())

    try:
        graph = get_research_graph()

        # Run research in background
        background_tasks.add_task(
            _run_research_job,
            query=request.query,
            thread_id=thread_id,
            user_id=request.user_id,
            max_sources=request.max_sources,
            max_depth=request.max_depth,
            focus_areas=request.focus_areas,
            query_type=request.query_type
        )

        logger.info(f"Research job started: {thread_id}")

        return ResearchResponse(
            thread_id=thread_id,
            status="processing",
            message=f"Research job started. Track progress at /api/research/{thread_id}"
        )

    except Exception as e:
        logger.error(f"Failed to start research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{thread_id}")
async def get_research_status(thread_id: str) -> Dict[str, Any]:
    """
    Get current status and progress of research job.

    Args:
        thread_id: Research session ID

    Returns:
        Current research state and progress
    """
    try:
        graph = get_research_graph()

        # Get cached state if available
        state = graph.get_state(thread_id)

        if state:
            return {
                "thread_id": thread_id,
                "current_phase": state.get("current_phase", "unknown"),
                "research_complete": state.get("research_complete", False),
                "progress": _calculate_progress(state),
                "report": state.get("final_report"),
                "summary": state.get("summary"),
                "citations": state.get("citations", []),
                "execution_time": state.get("execution_time", {}),
                "contradictions": len(state.get("contradictions", []))
            }
        else:
            raise HTTPException(status_code=404, detail="Research job not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get research status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{thread_id}/report")
async def get_research_report(
    thread_id: str,
    format: str = Query("markdown", regex="^(markdown|json|html)$")
) -> Dict[str, Any]:
    """
    Get complete research report.

    Args:
        thread_id: Research session ID
        format: Output format (markdown, json, html)

    Returns:
        Complete research report with citations
    """
    try:
        graph = get_research_graph()
        state = graph.get_state(thread_id)

        if not state:
            raise HTTPException(status_code=404, detail="Research job not found")

        if not state.get("research_complete"):
            raise HTTPException(
                status_code=202,
                detail="Research not yet complete"
            )

        report = {
            "thread_id": thread_id,
            "report": state.get("final_report", ""),
            "summary": state.get("summary", ""),
            "citations": state.get("citations", []),
            "bibliography": state.get("bibliography", []),
            "confidence_scores": state.get("confidence_scores", {}),
            "metadata": {
                "execution_time": state.get("execution_time", {}),
                "total_sources": len(state.get("ranked_sources", [])),
                "contradictions": len(state.get("contradictions", []))
            }
        }

        # Format conversion
        if format == "json":
            return report
        elif format == "html":
            # Would convert markdown to HTML here
            return {"report": _markdown_to_html(report["report"])}
        else:  # markdown (default)
            return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{thread_id}/citations")
async def get_research_citations(thread_id: str) -> Dict[str, Any]:
    """
    Get all citations and bibliography for research.

    Args:
        thread_id: Research session ID

    Returns:
        Citations and bibliography entries
    """
    try:
        graph = get_research_graph()
        state = graph.get_state(thread_id)

        if not state:
            raise HTTPException(status_code=404, detail="Research job not found")

        return {
            "thread_id": thread_id,
            "citations": state.get("citations", []),
            "bibliography": state.get("bibliography", []),
            "total_citations": len(state.get("citations", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get citations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{thread_id}/clarify")
async def provide_clarification(
    thread_id: str,
    feedback: str
) -> Dict[str, Any]:
    """
    Provide clarification or feedback to paused research.

    Args:
        thread_id: Research session ID
        feedback: User's clarification or feedback

    Returns:
        Updated research status
    """
    try:
        graph = get_research_graph()
        state = graph.get_state(thread_id)

        if not state:
            raise HTTPException(status_code=404, detail="Research job not found")

        if not state.get("requires_clarification"):
            raise HTTPException(
                status_code=400,
                detail="This research is not waiting for clarification"
            )

        # Update state with feedback and resume
        state["user_feedback"] = feedback
        state["requires_clarification"] = False

        # Resume research from planner phase
        logger.info(f"Resuming research with feedback: {thread_id}")

        return {
            "thread_id": thread_id,
            "status": "resumed",
            "message": "Research resumed with your feedback"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to provide clarification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health")
async def research_health() -> Dict[str, str]:
    """
    Check if research system is healthy and ready.

    Returns:
        Health status
    """
    try:
        graph = get_research_graph()
        return {
            "status": "healthy",
            "graph": "initialized",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Background task
async def _run_research_job(
    query: str,
    thread_id: str,
    user_id: Optional[str],
    max_sources: int,
    max_depth: int,
    focus_areas: Optional[list],
    query_type: str
):
    """
    Background task to run research.

    Args:
        query: Research query
        thread_id: Session ID
        user_id: User ID
        max_sources: Max sources
        max_depth: Research depth
        focus_areas: Focus areas
        query_type: Query type
    """
    try:
        graph = get_research_graph()

        result = await graph.research(
            query=query,
            thread_id=thread_id,
            user_id=user_id,
            max_sources=max_sources,
            max_depth=max_depth,
            focus_areas=focus_areas,
            query_type=query_type
        )

        logger.info(f"Research job completed: {thread_id}")

    except Exception as e:
        logger.error(f"Research job failed: {e}")


def _calculate_progress(state: Dict[str, Any]) -> float:
    """
    Calculate research progress (0.0-1.0).

    Args:
        state: Research state

    Returns:
        Progress percentage (0.0-1.0)
    """
    phase_weights = {
        "intake": 0.1,
        "planning": 0.15,
        "searching": 0.3,
        "fetching": 0.5,
        "ranking": 0.65,
        "synthesizing": 0.8,
        "writing": 0.95,
        "complete": 1.0
    }

    phase = state.get("current_phase", "intake")
    return phase_weights.get(phase, 0.0)


def _markdown_to_html(markdown: str) -> str:
    """
    Convert markdown to HTML (simplified).

    Args:
        markdown: Markdown text

    Returns:
        HTML version
    """
    try:
        import markdown
        return markdown.markdown(markdown)
    except ImportError:
        # Fallback: simple replacement
        html = markdown.replace("\n# ", "\n<h1>").replace("</h1>", "</h1>\n")
        return f"<div>{html}</div>"
