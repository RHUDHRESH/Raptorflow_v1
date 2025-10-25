"""
WebSocket Routes for Real-Time Agent Streaming

Provides real-time updates for long-running AI tasks:
- Research analysis progress
- Positioning generation
- ICP creation
- Content calendar generation
- Analytics computation

Uses FastAPI WebSockets + async event streaming.
"""

import json
import logging
import asyncio
from typing import Set, Optional
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

router = APIRouter()


class StreamEvent:
    """Represents a stream event sent to client"""

    def __init__(
        self,
        event_type: str,
        data: dict,
        timestamp: Optional[datetime] = None
    ):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()

    def to_json(self) -> str:
        """Serialize to JSON for transmission"""
        return json.dumps({
            "event": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        })


class ConnectionManager:
    """
    Manages WebSocket connections.

    Maintains active connections and broadcasts events.
    """

    def __init__(self):
        # Maps task_id -> set of connected WebSocket clients
        self.active_connections: dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        """Register a new WebSocket connection"""
        await websocket.accept()

        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()

        self.active_connections[task_id].add(websocket)
        logger.info(f"Client connected to task {task_id}")

    def disconnect(self, websocket: WebSocket, task_id: str):
        """Unregister a WebSocket connection"""
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)

            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

        logger.info(f"Client disconnected from task {task_id}")

    async def broadcast(self, task_id: str, event: StreamEvent):
        """Send event to all clients connected to this task"""
        if task_id not in self.active_connections:
            return

        message = event.to_json()
        dead_connections = set()

        for websocket in self.active_connections[task_id]:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                dead_connections.add(websocket)

        # Clean up dead connections
        for ws in dead_connections:
            self.disconnect(ws, task_id)

    async def broadcast_progress(
        self,
        task_id: str,
        stage: str,
        progress_percent: int,
        details: Optional[dict] = None
    ):
        """Convenience method to broadcast progress event"""
        event = StreamEvent(
            event_type="progress",
            data={
                "stage": stage,
                "progress": progress_percent,
                "details": details or {}
            }
        )
        await self.broadcast(task_id, event)

    async def broadcast_error(
        self,
        task_id: str,
        error_msg: str,
        error_type: str = "general"
    ):
        """Broadcast error event"""
        event = StreamEvent(
            event_type="error",
            data={
                "error": error_msg,
                "error_type": error_type
            }
        )
        await self.broadcast(task_id, event)

    async def broadcast_complete(
        self,
        task_id: str,
        result: dict,
        summary: Optional[dict] = None
    ):
        """Broadcast task completion"""
        event = StreamEvent(
            event_type="complete",
            data={
                "result": result,
                "summary": summary or {}
            }
        )
        await self.broadcast(task_id, event)


# Global connection manager
connection_manager = ConnectionManager()


# ============================================================================
# WebSocket Routes
# ============================================================================

@router.websocket("/ws/research/{business_id}")
async def websocket_research(websocket: WebSocket, business_id: str):
    """
    WebSocket endpoint for research progress updates.

    Client connects with: ws://api.example.com/ws/research/{business_id}

    Events sent:
    - progress: {stage, progress, details}
    - error: {error, error_type}
    - complete: {result, summary}
    """
    await connection_manager.connect(websocket, f"research_{business_id}")

    try:
        while True:
            # Wait for client to send a message (if any)
            data = await websocket.receive_text()
            # Echo back if client sends anything
            await websocket.send_text(json.dumps({
                "event": "ack",
                "data": {"message": "Connected to research stream"}
            }))

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, f"research_{business_id}")
        logger.info(f"Research stream disconnected: {business_id}")

    except Exception as e:
        logger.error(f"WebSocket error in research: {e}")
        connection_manager.disconnect(websocket, f"research_{business_id}")


@router.websocket("/ws/positioning/{business_id}")
async def websocket_positioning(websocket: WebSocket, business_id: str):
    """
    WebSocket endpoint for positioning generation progress.

    Events: progress, error, complete
    """
    await connection_manager.connect(websocket, f"positioning_{business_id}")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({
                "event": "ack",
                "data": {"message": "Connected to positioning stream"}
            }))

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, f"positioning_{business_id}")

    except Exception as e:
        logger.error(f"WebSocket error in positioning: {e}")
        connection_manager.disconnect(websocket, f"positioning_{business_id}")


@router.websocket("/ws/icps/{business_id}")
async def websocket_icps(websocket: WebSocket, business_id: str):
    """
    WebSocket endpoint for ICP generation progress.

    Events: progress, error, complete
    """
    await connection_manager.connect(websocket, f"icps_{business_id}")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({
                "event": "ack",
                "data": {"message": "Connected to ICP stream"}
            }))

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, f"icps_{business_id}")

    except Exception as e:
        logger.error(f"WebSocket error in ICPs: {e}")
        connection_manager.disconnect(websocket, f"icps_{business_id}")


@router.websocket("/ws/content/{business_id}")
async def websocket_content(websocket: WebSocket, business_id: str):
    """
    WebSocket endpoint for content calendar generation progress.

    Events: progress, error, complete
    """
    await connection_manager.connect(websocket, f"content_{business_id}")

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({
                "event": "ack",
                "data": {"message": "Connected to content stream"}
            }))

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, f"content_{business_id}")

    except Exception as e:
        logger.error(f"WebSocket error in content: {e}")
        connection_manager.disconnect(websocket, f"content_{business_id}")


# ============================================================================
# Helper Functions for Agents to Use
# ============================================================================

async def emit_progress(
    business_id: str,
    stream_type: str,  # "research", "positioning", "icps", "content"
    stage: str,
    progress_percent: int,
    details: Optional[dict] = None
):
    """
    Emit progress event from agent code.

    Usage in agents:
        await emit_progress("biz-123", "research", "competitor_analysis", 33, {
            "competitors_found": 15
        })

    Args:
        business_id: Business being analyzed
        stream_type: Type of stream
        stage: Current stage of processing
        progress_percent: 0-100 progress
        details: Optional metadata
    """
    task_id = f"{stream_type}_{business_id}"
    await connection_manager.broadcast_progress(
        task_id, stage, progress_percent, details
    )


async def emit_error(
    business_id: str,
    stream_type: str,
    error_msg: str,
    error_type: str = "general"
):
    """
    Emit error event from agent code.

    Usage in agents:
        await emit_error("biz-123", "research", "Failed to fetch competitor data")
    """
    task_id = f"{stream_type}_{business_id}"
    await connection_manager.broadcast_error(task_id, error_msg, error_type)


async def emit_complete(
    business_id: str,
    stream_type: str,
    result: dict,
    summary: Optional[dict] = None
):
    """
    Emit task completion event from agent code.

    Usage in agents:
        await emit_complete("biz-123", "research", {
            "competitor_ladder": [...],
            "sostac": {...}
        }, {"duration": 45.2})
    """
    task_id = f"{stream_type}_{business_id}"
    await connection_manager.broadcast_complete(task_id, result, summary)


# ============================================================================
# Example Usage in Agent (Show Pattern)
# ============================================================================

async def example_research_agent_with_streaming(business_id: str, ai_provider_manager):
    """
    Example of how to integrate streaming into agent code.

    Agents should:
    1. Emit progress at each stage
    2. Emit errors if anything fails
    3. Emit complete with final results
    """
    try:
        # Stage 1: Situation Analysis
        await emit_progress(
            business_id, "research",
            "situation_analysis",
            10,
            {"stage": "Starting situation analysis"}
        )

        # ... run situation analysis ...
        situation_result = {}  # AI response

        await emit_progress(
            business_id, "research",
            "situation_analysis",
            25,
            {"items_analyzed": len(situation_result)}
        )

        # Stage 2: Competitor Intelligence
        await emit_progress(
            business_id, "research",
            "competitor_intelligence",
            40,
            {"stage": "Analyzing competitors"}
        )

        competitor_result = {}  # AI response

        await emit_progress(
            business_id, "research",
            "competitor_intelligence",
            55,
            {"competitors_found": 15}
        )

        # Stage 3: SOSTAC Analysis
        await emit_progress(
            business_id, "research",
            "sostac_analysis",
            70,
            {"stage": "Building SOSTAC framework"}
        )

        sostac_result = {}  # AI response

        # Complete
        await emit_progress(business_id, "research", "complete", 100)

        await emit_complete(
            business_id, "research",
            {
                "situation": situation_result,
                "competitors": competitor_result,
                "sostac": sostac_result
            },
            {
                "total_duration": 120.5,
                "stages_completed": 3,
                "total_cost": 1.25
            }
        )

    except Exception as e:
        logger.error(f"Research agent error: {e}")
        await emit_error(
            business_id, "research",
            str(e),
            "agent_failure"
        )
