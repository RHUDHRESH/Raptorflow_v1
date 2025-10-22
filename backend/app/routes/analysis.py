"""Analysis Orchestration & Streaming API Routes"""
import logging
import uuid
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncGenerator, Optional

from ..models.strategy import Strategy, ContextItem
from ..db.session import get_db
from ..models.token_ledger import TokenLedger
from ..models.auth import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])


# ============================================================================
# Analysis Event Streaming
# ============================================================================

async def generate_analysis_events(
    workspace_id: str,
    strategy_id: str,
    user_id: str,
    db: Session
) -> AsyncGenerator[str, None]:
    """
    Generate analysis events via Server-Sent Events (SSE)
    Streams real-time agent processing updates to client
    """
    try:
        # Get context items for analysis
        context_items = db.query(ContextItem).filter(
            ContextItem.workspace_id == workspace_id
        ).all()

        if not context_items:
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': 'No context items found'}, 'timestamp': int(datetime.now().timestamp() * 1000)})}\n\n"
            return

        # Start event
        yield f"data: {json.dumps({'type': 'start', 'data': {'message': 'Analysis started'}, 'timestamp': int(datetime.now().timestamp() * 1000)})}\n\n"

        # Simulate agent processing stages (in production, this would call actual agents)
        stages = [
            {"agent": "ContextProcessor", "step": 1, "message": "Processing context items..."},
            {"agent": "ContextProcessor", "step": 2, "message": "Extracting text and metadata..."},
            {"agent": "JTBDExtractor", "step": 3, "message": "Identifying Jobs-to-be-Done..."},
            {"agent": "ICPBuilder", "step": 4, "message": "Building Ideal Customer Profiles..."},
            {"agent": "ChannelMapper", "step": 5, "message": "Mapping marketing channels..."},
            {"agent": "ExplanationAgent", "step": 6, "message": "Generating explanations..."},
        ]

        # Track tokens for this analysis
        tokens_used = 0

        for idx, stage in enumerate(stages):
            # Thinking phase
            yield f"data: {json.dumps({'type': 'thinking', 'data': {'message': stage['message']}, 'agent': stage['agent'], 'step': stage['step'], 'timestamp': int(datetime.now().timestamp() * 1000)})}\n\n"
            await asyncio.sleep(0.5)  # Simulate processing

            # Progress phase
            yield f"data: {json.dumps({'type': 'progress', 'data': {'percentage': int((idx / len(stages)) * 100)}, 'agent': stage['agent'], 'timestamp': int(datetime.now().timestamp() * 1000)})}\n\n"

            # Tool call phase (simulate tool usage)
            tokens_used += 500  # Simulate token consumption
            yield f"data: {json.dumps({'type': 'tool_call', 'data': {'tool': 'language_model', 'tokens': 500, 'total_tokens': tokens_used}, 'agent': stage['agent'], 'step': stage['step'], 'timestamp': int(datetime.now().timestamp() * 1000)})}\n\n"
            await asyncio.sleep(0.3)

            # Result phase
            yield f"data: {json.dumps({'type': 'result', 'data': {'message': f'{stage[\"agent\"]} stage complete', 'items_processed': len(context_items)}, 'agent': stage['agent'], 'timestamp': int(datetime.now().timestamp() * 1000)})}\n\n"
            await asyncio.sleep(0.2)

        # Save token usage to ledger
        try:
            token_entry = TokenLedger(
                id=str(uuid.uuid4()),
                user_id=user_id,
                workspace_id=workspace_id,
                strategy_id=strategy_id,
                tokens_used=tokens_used,
                cost_usd=tokens_used * 0.001 / 1000,  # Rough estimate: $0.001 per 1K tokens
                agent_name="AnalysisPipeline",
                request_type="analysis_submission",
                metadata={
                    "stages_completed": len(stages),
                    "context_items": len(context_items),
                }
            )
            db.add(token_entry)
            db.commit()
            logger.info(f"Token entry created: {tokens_used} tokens used")
        except Exception as e:
            logger.error(f"Failed to save token usage: {str(e)}")

        # Completion event
        yield f"data: {json.dumps({'type': 'done', 'data': {'message': 'Analysis completed', 'total_tokens': tokens_used, 'cost': tokens_used * 0.001 / 1000}, 'timestamp': int(datetime.now().timestamp() * 1000)})}\n\n"

    except Exception as e:
        logger.exception(f"Error in analysis streaming: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}, 'timestamp': int(datetime.now().timestamp() * 1000)})}\n\n"


@router.post("/strategies/{strategy_id}/analysis", response_model=dict)
async def submit_analysis(
    strategy_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """
    Submit analysis request for a strategy

    Returns analysis_id for tracking and streaming
    """
    try:
        # Get strategy
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        # Create analysis ID
        analysis_id = str(uuid.uuid4())

        logger.info(f"Analysis submitted for strategy {strategy_id}, analysis_id: {analysis_id}")

        return {
            "data": {
                "analysis_id": analysis_id,
                "strategy_id": strategy_id,
                "status": "processing",
                "created_at": datetime.now().isoformat(),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error submitting analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit analysis: {str(e)}"
        )


@router.get("/strategies/{strategy_id}/analysis/stream")
async def stream_analysis(
    strategy_id: str,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """
    Stream analysis events via Server-Sent Events (SSE)

    Client can listen to real-time analysis progress
    """
    try:
        # Get strategy
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        # Generate events
        async def event_generator():
            async for event in generate_analysis_events(
                workspace_id=strategy.id,
                strategy_id=strategy_id,
                user_id=user_id or "anonymous",
                db=db
            ):
                yield event

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error streaming analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream analysis: {str(e)}"
        )


@router.get("/analysis/{analysis_id}/status")
async def get_analysis_status(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current analysis status

    Returns progress, completion status, and results
    """
    try:
        # In a real implementation, this would query an Analysis model
        # For now, return mock data
        return {
            "data": {
                "analysis_id": analysis_id,
                "status": "completed",
                "progress": 100,
                "total_events": 12,
                "tokens_used": 3000,
                "cost_usd": 0.003,
                "completed_at": datetime.now().isoformat(),
            }
        }

    except Exception as e:
        logger.exception(f"Error getting analysis status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis status: {str(e)}"
        )


@router.get("/strategies/{strategy_id}/analysis-results")
async def get_analysis_results(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete analysis results

    Returns all generated content (JTBDs, ICPs, channels, explanations)
    """
    try:
        # Get strategy
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        # Return mock results
        return {
            "data": {
                "strategy_id": strategy_id,
                "jtbds_count": 5,
                "icps_count": 3,
                "channels_count": 12,
                "explanations_count": 20,
                "status": "ready",
                "generated_at": datetime.now().isoformat(),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting analysis results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis results: {str(e)}"
        )


# ============================================================================
# Context Items API (REST endpoints)
# ============================================================================

@router.post("/strategies/{strategy_id}/context-items")
async def add_context_item(
    strategy_id: str,
    type: str,
    content: str,
    db: Session = Depends(get_db)
):
    """
    Add context item to strategy (text, URL, or file)

    Supports multiple content types for analysis
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        context_item = ContextItem(
            id=str(uuid.uuid4()),
            workspace_id=strategy.id,
            item_type=type,
            source="api",
            raw_content=content,
            extracted_text=content,
            metadata={"added_via": "api"},
        )

        db.add(context_item)
        db.commit()
        db.refresh(context_item)

        return {
            "data": {
                "id": context_item.id,
                "type": context_item.item_type,
                "source": context_item.source,
                "created_at": context_item.created_at.isoformat() if context_item.created_at else None,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error adding context item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add context item: {str(e)}"
        )


@router.get("/strategies/{strategy_id}/context-items")
async def list_context_items(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """
    List all context items for a strategy
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        items = db.query(ContextItem).filter(
            ContextItem.workspace_id == strategy.id
        ).all()

        return {
            "data": [
                {
                    "id": item.id,
                    "type": item.item_type,
                    "source": item.source,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                }
                for item in items
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error listing context items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list context items: {str(e)}"
        )


@router.delete("/strategies/{strategy_id}/context-items/{item_id}")
async def delete_context_item(
    strategy_id: str,
    item_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a context item
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        item = db.query(ContextItem).filter(
            ContextItem.id == item_id,
            ContextItem.workspace_id == strategy.id
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Context item not found"
            )

        db.delete(item)
        db.commit()

        return {"success": True, "deleted_id": item_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting context item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete context item: {str(e)}"
        )


# ============================================================================
# Workspace/Strategy Management
# ============================================================================

@router.post("/strategies", response_model=dict)
async def create_strategy(
    payload: dict,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """
    Create a new strategy workspace

    Required fields:
    - workspace_id: Associated workspace
    - name: Strategy name
    - description (optional): Strategy description
    """
    try:
        workspace_id = payload.get("workspace_id")
        name = payload.get("name")
        description = payload.get("description", "")

        if not workspace_id or not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="workspace_id and name are required"
            )

        strategy = Strategy(
            id=str(uuid.uuid4()),
            business_id=workspace_id,
            name=name,
            description=description,
            status="context_intake",
        )

        db.add(strategy)
        db.commit()
        db.refresh(strategy)

        logger.info(f"Strategy created: {strategy.id}")

        return {
            "data": {
                "id": strategy.id,
                "name": strategy.name,
                "status": strategy.status,
                "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create strategy: {str(e)}"
        )


@router.get("/strategies/{strategy_id}")
async def get_strategy(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """
    Get strategy details
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        return {
            "data": {
                "id": strategy.id,
                "name": strategy.name,
                "status": strategy.status,
                "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
                "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy: {str(e)}"
        )


@router.patch("/strategies/{strategy_id}")
async def update_strategy(
    strategy_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Update strategy
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        if "name" in payload:
            strategy.name = payload["name"]
        if "description" in payload:
            strategy.description = payload["description"]

        db.commit()
        db.refresh(strategy)

        return {
            "data": {
                "id": strategy.id,
                "name": strategy.name,
                "status": strategy.status,
                "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update strategy: {str(e)}"
        )


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete strategy and all associated data
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )

        # Delete associated context items
        db.query(ContextItem).filter(
            ContextItem.workspace_id == strategy.id
        ).delete()

        # Delete strategy
        db.delete(strategy)
        db.commit()

        return {"success": True, "deleted_id": strategy_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete strategy: {str(e)}"
        )


@router.get("/strategies")
async def list_strategies(
    workspace_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all strategies (optionally filtered by workspace)
    """
    try:
        query = db.query(Strategy)

        if workspace_id:
            query = query.filter(Strategy.business_id == workspace_id)

        strategies = query.all()

        return {
            "data": [
                {
                    "id": s.id,
                    "name": s.name,
                    "status": s.status,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in strategies
            ]
        }

    except Exception as e:
        logger.exception(f"Error listing strategies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list strategies: {str(e)}"
        )
