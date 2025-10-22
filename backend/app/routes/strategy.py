"""Strategy Workspace API Routes"""
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.strategy import (
    Strategy, ContextItem, JTBD, ICP, Channel, Citation, Explanation,
    ContextItemRequest, ContextItemResponse, JTBDRequest, JTBDResponse,
    ICPRequest, ICPResponse, ChannelRequest, ChannelResponse,
    ExplanationResponse, StrategyResponse, ContextItemType
)
from ..db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/strategy", tags=["strategy"])


# ============================================================================
# Context Management Endpoints
# ============================================================================

@router.post("/{workspace_id}/context/add-text", response_model=ContextItemResponse)
async def add_text_context(
    workspace_id: str,
    request: ContextItemRequest,
    db: Session = Depends(get_db)
):
    """Add text context to strategy workspace"""
    try:
        context_item = ContextItem(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            item_type=ContextItemType.TEXT,
            source="user_input",
            raw_content=request.content,
            extracted_text=request.content,  # Text is already extracted
            metadata=request.metadata,
        )

        db.add(context_item)
        db.commit()
        db.refresh(context_item)

        return ContextItemResponse(
            id=context_item.id,
            item_type=context_item.item_type,
            source=context_item.source,
            extracted_text=context_item.extracted_text,
            topics=context_item.topics,
            entities=context_item.entities,
            keywords=context_item.keywords,
            sentiment=context_item.sentiment,
            created_at=context_item.created_at,
        )

    except Exception as e:
        logger.exception(f"Error adding text context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add context: {str(e)}"
        )


@router.post("/{workspace_id}/context/upload-file", response_model=ContextItemResponse)
async def upload_file_context(
    workspace_id: str,
    file: UploadFile = File(...),
    metadata: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Upload file context (image, PDF, video, audio)"""
    try:
        # Determine item type based on file extension
        file_ext = file.filename.split(".")[-1].lower()
        item_type_map = {
            "jpg": ContextItemType.FILE_IMAGE,
            "jpeg": ContextItemType.FILE_IMAGE,
            "png": ContextItemType.FILE_IMAGE,
            "gif": ContextItemType.FILE_IMAGE,
            "pdf": ContextItemType.FILE_PDF,
            "mp4": ContextItemType.FILE_VIDEO,
            "webm": ContextItemType.FILE_VIDEO,
            "mov": ContextItemType.FILE_VIDEO,
            "mp3": ContextItemType.FILE_AUDIO,
            "wav": ContextItemType.FILE_AUDIO,
            "m4a": ContextItemType.FILE_AUDIO,
        }

        item_type = item_type_map.get(file_ext, ContextItemType.FILE_PDF)

        # Save file to storage (implementation depends on storage choice)
        file_path = f"/uploads/{workspace_id}/{uuid.uuid4()}_{file.filename}"

        # Read file content
        content = await file.read()

        context_item = ContextItem(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            item_type=item_type,
            source="uploaded_file",
            raw_content=file.filename,
            file_path=file_path,
            metadata={"original_filename": file.filename},
        )

        db.add(context_item)
        db.commit()
        db.refresh(context_item)

        return ContextItemResponse(
            id=context_item.id,
            item_type=context_item.item_type,
            source=context_item.source,
            extracted_text=context_item.extracted_text,
            topics=context_item.topics,
            entities=context_item.entities,
            keywords=context_item.keywords,
            sentiment=context_item.sentiment,
            created_at=context_item.created_at,
        )

    except Exception as e:
        logger.exception(f"Error uploading file context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post("/{workspace_id}/context/add-link", response_model=ContextItemResponse)
async def add_url_context(
    workspace_id: str,
    request: ContextItemRequest,
    db: Session = Depends(get_db)
):
    """Add URL/link context"""
    try:
        context_item = ContextItem(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            item_type=ContextItemType.URL,
            source="web_link",
            raw_content=request.content,
            url=request.content,
            metadata=request.metadata,
        )

        db.add(context_item)
        db.commit()
        db.refresh(context_item)

        return ContextItemResponse(
            id=context_item.id,
            item_type=context_item.item_type,
            source=context_item.source,
            extracted_text=context_item.extracted_text,
            topics=context_item.topics,
            entities=context_item.entities,
            keywords=context_item.keywords,
            sentiment=context_item.sentiment,
            created_at=context_item.created_at,
        )

    except Exception as e:
        logger.exception(f"Error adding URL context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add URL: {str(e)}"
        )


@router.get("/{workspace_id}/context", response_model=List[ContextItemResponse])
async def list_context_items(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """List all context items in workspace"""
    try:
        items = db.query(ContextItem).filter(
            ContextItem.workspace_id == workspace_id
        ).all()

        return [
            ContextItemResponse(
                id=item.id,
                item_type=item.item_type,
                source=item.source,
                extracted_text=item.extracted_text,
                topics=item.topics,
                entities=item.entities,
                keywords=item.keywords,
                sentiment=item.sentiment,
                created_at=item.created_at,
            )
            for item in items
        ]

    except Exception as e:
        logger.exception(f"Error listing context items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list context items: {str(e)}"
        )


@router.delete("/{workspace_id}/context/{context_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_context_item(
    workspace_id: str,
    context_id: str,
    db: Session = Depends(get_db)
):
    """Delete a context item"""
    try:
        item = db.query(ContextItem).filter(
            ContextItem.id == context_id,
            ContextItem.workspace_id == workspace_id
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Context item not found"
            )

        db.delete(item)
        db.commit()

    except Exception as e:
        logger.exception(f"Error deleting context item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete context item: {str(e)}"
        )


# ============================================================================
# Analysis Orchestration
# ============================================================================

@router.post("/{workspace_id}/analyze")
async def analyze_strategy(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """
    Run full strategy analysis pipeline (5-stage agent orchestration)

    This endpoint triggers the 5-stage analysis pipeline:
    1. ContextProcessorAgent - Processes text/files/URLs and performs NLP analysis
    2. JTBDExtractionAgent - Clusters context and extracts Jobs-to-be-Done
    3. ICPBuilderAgent - Generates Ideal Customer Profiles from context
    4. ChannelMapperAgent - Maps marketing channels and AISAS stages
    5. ExplanationAgent - Generates rationales with evidence citations

    The agents are imported here to avoid circular imports.
    """
    try:
        from backend.agents.context_processor_agent import create_context_processor_agent
        from backend.agents.jtbd_extraction_agent import create_jtbd_extraction_agent
        from backend.agents.icp_builder_agent import create_icp_builder_agent
        from backend.agents.channel_mapper_agent import create_channel_mapper_agent
        from backend.agents.explanation_agent import create_explanation_agent

        # Get context items
        context_items = db.query(ContextItem).filter(
            ContextItem.workspace_id == workspace_id
        ).all()

        if not context_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No context items found for analysis"
            )

        logger.info(f"Starting analysis pipeline for workspace {workspace_id}")

        # Stage 1: Process context
        context_processor = create_context_processor_agent()
        context_state = {
            "context": {
                "workspace_id": workspace_id,
                "context_items": [
                    {
                        "id": item.id,
                        "item_type": item.item_type,
                        "source": item.source,
                        "content": item.raw_content,
                    }
                    for item in context_items
                ]
            }
        }
        context_result = await context_processor.app.ainvoke(context_state)

        # Stage 2: Extract JTBD
        jtbd_extractor = create_jtbd_extraction_agent()
        jtbd_state = {
            "context": {
                "workspace_id": workspace_id,
                "processed_context_items": context_result.get("results", {}).get("processed_context_items", []),
            }
        }
        jtbd_result = await jtbd_extractor.app.ainvoke(jtbd_state)

        # Stage 3: Build ICPs
        icp_builder = create_icp_builder_agent()
        icp_state = {
            "context": {
                "workspace_id": workspace_id,
                "processed_context_items": context_result.get("results", {}).get("processed_context_items", []),
                "extracted_jtbds": jtbd_result.get("results", {}).get("extracted_jtbds", []),
            }
        }
        icp_result = await icp_builder.app.ainvoke(icp_state)

        # Stage 4: Map channels
        channel_mapper = create_channel_mapper_agent()
        channel_state = {
            "context": {
                "workspace_id": workspace_id,
                "built_icps": icp_result.get("results", {}).get("built_icps", []),
                "extracted_jtbds": jtbd_result.get("results", {}).get("extracted_jtbds", []),
            }
        }
        channel_result = await channel_mapper.app.ainvoke(channel_state)

        # Stage 5: Generate explanations
        explanation_agent_inst = create_explanation_agent()
        explanation_state = {
            "context": {
                "workspace_id": workspace_id,
                "processed_context_items": context_result.get("results", {}).get("processed_context_items", []),
                "extracted_jtbds": jtbd_result.get("results", {}).get("extracted_jtbds", []),
                "built_icps": icp_result.get("results", {}).get("built_icps", []),
                "mapped_channels": channel_result.get("results", {}).get("mapped_channels", []),
            }
        }
        explanation_result = await explanation_agent_inst.app.ainvoke(explanation_state)

        # Update workspace status
        workspace = db.query(Strategy).filter(Strategy.id == workspace_id).first()
        if workspace:
            workspace.status = "ready_for_moves"
            workspace.context_processed = True
            workspace.jtbds_extracted = True
            workspace.icps_built = True
            workspace.channels_mapped = True
            workspace.explanations_generated = True
            db.commit()

        return {
            "success": True,
            "workspace_id": workspace_id,
            "analysis": {
                "context_items_processed": context_result.get("results", {}).get("item_count", 0),
                "jtbds_extracted": jtbd_result.get("results", {}).get("jtbd_count", 0),
                "icps_built": icp_result.get("results", {}).get("icp_count", 0),
                "channels_mapped": channel_result.get("results", {}).get("channel_count", 0),
                "explanations_generated": explanation_result.get("results", {}).get("explanation_count", 0),
            },
            "message": "Analysis pipeline completed successfully"
        }

    except Exception as e:
        logger.exception(f"Error in strategy analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


# ============================================================================
# JTBD Management
# ============================================================================

@router.get("/{workspace_id}/jobs", response_model=List[JTBDResponse])
async def list_jtbds(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """List all JTBDs in workspace"""
    try:
        jtbds = db.query(JTBD).filter(JTBD.workspace_id == workspace_id).all()
        return [
            JTBDResponse(
                id=j.id,
                why=j.why,
                circumstances=j.circumstances,
                forces=j.forces,
                anxieties=j.anxieties,
                confidence_score=j.confidence_score,
                evidence_citations=j.evidence_citations,
                status=j.status,
            )
            for j in jtbds
        ]
    except Exception as e:
        logger.exception(f"Error listing JTBDs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list JTBDs: {str(e)}"
        )


@router.put("/{workspace_id}/jobs/{job_id}", response_model=JTBDResponse)
async def update_jtbd(
    workspace_id: str,
    job_id: str,
    request: JTBDRequest,
    db: Session = Depends(get_db)
):
    """Update a JTBD"""
    try:
        jtbd = db.query(JTBD).filter(
            JTBD.id == job_id,
            JTBD.workspace_id == workspace_id
        ).first()

        if not jtbd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="JTBD not found"
            )

        jtbd.why = request.why
        jtbd.circumstances = request.circumstances
        jtbd.forces = request.forces
        jtbd.anxieties = request.anxieties

        db.commit()
        db.refresh(jtbd)

        return JTBDResponse(
            id=jtbd.id,
            why=jtbd.why,
            circumstances=jtbd.circumstances,
            forces=jtbd.forces,
            anxieties=jtbd.anxieties,
            confidence_score=jtbd.confidence_score,
            evidence_citations=jtbd.evidence_citations,
            status=jtbd.status,
        )

    except Exception as e:
        logger.exception(f"Error updating JTBD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update JTBD: {str(e)}"
        )


@router.delete("/{workspace_id}/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_jtbd(
    workspace_id: str,
    job_id: str,
    db: Session = Depends(get_db)
):
    """Delete a JTBD"""
    try:
        jtbd = db.query(JTBD).filter(
            JTBD.id == job_id,
            JTBD.workspace_id == workspace_id
        ).first()

        if not jtbd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="JTBD not found"
            )

        db.delete(jtbd)
        db.commit()

    except Exception as e:
        logger.exception(f"Error deleting JTBD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete JTBD: {str(e)}"
        )


@router.post("/{workspace_id}/jobs/merge")
async def merge_jtbds(
    workspace_id: str,
    job_id_1: str,
    job_id_2: str,
    merged_jtbd: JTBDRequest,
    db: Session = Depends(get_db)
):
    """Merge two JTBDs"""
    try:
        jtbd1 = db.query(JTBD).filter(
            JTBD.id == job_id_1,
            JTBD.workspace_id == workspace_id
        ).first()
        jtbd2 = db.query(JTBD).filter(
            JTBD.id == job_id_2,
            JTBD.workspace_id == workspace_id
        ).first()

        if not jtbd1 or not jtbd2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both JTBDs not found"
            )

        # Create merged JTBD
        merged = JTBD(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            why=merged_jtbd.why,
            circumstances=merged_jtbd.circumstances,
            forces=merged_jtbd.forces,
            anxieties=merged_jtbd.anxieties,
        )

        # Delete originals
        db.delete(jtbd1)
        db.delete(jtbd2)
        db.add(merged)
        db.commit()

        return {"success": True, "merged_id": merged.id}

    except Exception as e:
        logger.exception(f"Error merging JTBDs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to merge JTBDs: {str(e)}"
        )


# ============================================================================
# ICP Management
# ============================================================================

@router.get("/{workspace_id}/icps", response_model=List[ICPResponse])
async def list_icps(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """List all ICPs in workspace"""
    try:
        icps = db.query(ICP).filter(ICP.workspace_id == workspace_id).all()
        return [
            ICPResponse(
                id=i.id,
                name=i.name,
                avatar_url=i.avatar_url,
                avatar_color=i.avatar_color,
                traits=i.traits,
                pain_points=i.pain_points,
                behaviors=i.behaviors,
                health_score=i.health_score,
                mood=i.mood,
                confidence_score=i.confidence_score,
            )
            for i in icps
        ]
    except Exception as e:
        logger.exception(f"Error listing ICPs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list ICPs: {str(e)}"
        )


@router.put("/{workspace_id}/icps/{icp_id}", response_model=ICPResponse)
async def update_icp(
    workspace_id: str,
    icp_id: str,
    request: ICPRequest,
    db: Session = Depends(get_db)
):
    """Update an ICP"""
    try:
        icp = db.query(ICP).filter(
            ICP.id == icp_id,
            ICP.workspace_id == workspace_id
        ).first()

        if not icp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ICP not found"
            )

        icp.name = request.name
        icp.traits = request.traits
        icp.pain_points = request.pain_points
        icp.behaviors = request.behaviors

        db.commit()
        db.refresh(icp)

        return ICPResponse(
            id=icp.id,
            name=icp.name,
            avatar_url=icp.avatar_url,
            avatar_color=icp.avatar_color,
            traits=icp.traits,
            pain_points=icp.pain_points,
            behaviors=icp.behaviors,
            health_score=icp.health_score,
            mood=icp.mood,
            confidence_score=icp.confidence_score,
        )

    except Exception as e:
        logger.exception(f"Error updating ICP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update ICP: {str(e)}"
        )


@router.delete("/{workspace_id}/icps/{icp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_icp(
    workspace_id: str,
    icp_id: str,
    db: Session = Depends(get_db)
):
    """Delete an ICP"""
    try:
        icp = db.query(ICP).filter(
            ICP.id == icp_id,
            ICP.workspace_id == workspace_id
        ).first()

        if not icp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ICP not found"
            )

        db.delete(icp)
        db.commit()

    except Exception as e:
        logger.exception(f"Error deleting ICP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete ICP: {str(e)}"
        )


# ============================================================================
# Channel Management
# ============================================================================

@router.get("/{workspace_id}/channels", response_model=List[ChannelResponse])
async def list_channels(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """List all channel recommendations in workspace"""
    try:
        channels = db.query(Channel).filter(Channel.workspace_id == workspace_id).all()
        return [
            ChannelResponse(
                id=c.id,
                channel_name=c.channel_name,
                aisas_stage=c.aisas_stage,
                content_type=c.content_type,
                cadence=c.cadence,
                tone=c.tone,
                confidence_score=c.confidence_score,
                reasoning=c.reasoning,
            )
            for c in channels
        ]
    except Exception as e:
        logger.exception(f"Error listing channels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list channels: {str(e)}"
        )


@router.put("/{workspace_id}/channels/{icp_id}/{job_id}", response_model=ChannelResponse)
async def update_channel(
    workspace_id: str,
    icp_id: str,
    job_id: str,
    request: ChannelRequest,
    db: Session = Depends(get_db)
):
    """Update a channel in the matrix"""
    try:
        channel = db.query(Channel).filter(
            Channel.workspace_id == workspace_id,
            Channel.icp_id == icp_id,
            Channel.jtbd_id == job_id,
            Channel.channel_name == request.channel_name,
        ).first()

        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )

        channel.aisas_stage = request.aisas_stage

        db.commit()
        db.refresh(channel)

        return ChannelResponse(
            id=channel.id,
            channel_name=channel.channel_name,
            aisas_stage=channel.aisas_stage,
            content_type=channel.content_type,
            cadence=channel.cadence,
            tone=channel.tone,
            confidence_score=channel.confidence_score,
            reasoning=channel.reasoning,
        )

    except Exception as e:
        logger.exception(f"Error updating channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update channel: {str(e)}"
        )


# ============================================================================
# Explanations & Rationales
# ============================================================================

@router.get("/{workspace_id}/explanations", response_model=List[ExplanationResponse])
async def list_explanations(
    workspace_id: str,
    entity_type: Optional[str] = None,
    explanation_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List explanations with optional filtering"""
    try:
        query = db.query(Explanation).filter(Explanation.workspace_id == workspace_id)

        if entity_type:
            query = query.filter(Explanation.entity_type == entity_type)

        if explanation_type:
            query = query.filter(Explanation.explanation_type == explanation_type)

        explanations = query.all()

        return [
            ExplanationResponse(
                id=e.id,
                entity_type=e.entity_type,
                entity_id=e.entity_id,
                title=e.title,
                rationale=e.rationale,
                explanation_type=e.explanation_type,
                confidence_score=e.confidence_score,
                citation_ids=e.citation_ids,
            )
            for e in explanations
        ]

    except Exception as e:
        logger.exception(f"Error listing explanations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list explanations: {str(e)}"
        )


# ============================================================================
# Workspace Management
# ============================================================================

@router.get("/{workspace_id}", response_model=StrategyResponse)
async def get_strategy_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get complete strategy workspace"""
    try:
        workspace = db.query(Strategy).filter(Strategy.id == workspace_id).first()

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        # Get all related entities
        context_items = db.query(ContextItem).filter(
            ContextItem.workspace_id == workspace_id
        ).all()
        jtbds = db.query(JTBD).filter(JTBD.workspace_id == workspace_id).all()
        icps = db.query(ICP).filter(ICP.workspace_id == workspace_id).all()
        channels = db.query(Channel).filter(Channel.workspace_id == workspace_id).all()
        explanations = db.query(Explanation).filter(
            Explanation.workspace_id == workspace_id
        ).all()

        return StrategyResponse(
            id=workspace.id,
            business_id=workspace.business_id,
            name=workspace.name,
            status=workspace.status,
            context_items=[
                ContextItemResponse(
                    id=c.id,
                    item_type=c.item_type,
                    source=c.source,
                    extracted_text=c.extracted_text,
                    topics=c.topics,
                    entities=c.entities,
                    keywords=c.keywords,
                    sentiment=c.sentiment,
                    created_at=c.created_at,
                )
                for c in context_items
            ],
            jtbds=[
                JTBDResponse(
                    id=j.id,
                    why=j.why,
                    circumstances=j.circumstances,
                    forces=j.forces,
                    anxieties=j.anxieties,
                    confidence_score=j.confidence_score,
                    evidence_citations=j.evidence_citations,
                    status=j.status,
                )
                for j in jtbds
            ],
            icps=[
                ICPResponse(
                    id=i.id,
                    name=i.name,
                    avatar_url=i.avatar_url,
                    avatar_color=i.avatar_color,
                    traits=i.traits,
                    pain_points=i.pain_points,
                    behaviors=i.behaviors,
                    health_score=i.health_score,
                    mood=i.mood,
                    confidence_score=i.confidence_score,
                )
                for i in icps
            ],
            channels=[
                ChannelResponse(
                    id=c.id,
                    channel_name=c.channel_name,
                    aisas_stage=c.aisas_stage,
                    content_type=c.content_type,
                    cadence=c.cadence,
                    tone=c.tone,
                    confidence_score=c.confidence_score,
                    reasoning=c.reasoning,
                )
                for c in channels
            ],
            explanations=[
                ExplanationResponse(
                    id=e.id,
                    entity_type=e.entity_type,
                    entity_id=e.entity_id,
                    title=e.title,
                    rationale=e.rationale,
                    explanation_type=e.explanation_type,
                    confidence_score=e.confidence_score,
                    citation_ids=e.citation_ids,
                )
                for e in explanations
            ],
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
        )

    except Exception as e:
        logger.exception(f"Error getting workspace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workspace: {str(e)}"
        )


@router.post("/create", response_model=dict)
async def create_workspace(
    business_id: str,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new strategy workspace"""
    try:
        workspace = Strategy(
            id=str(uuid.uuid4()),
            business_id=business_id,
            name=name or f"Strategy {datetime.now().strftime('%Y-%m-%d')}",
            status="context_intake",
        )

        db.add(workspace)
        db.commit()
        db.refresh(workspace)

        return {
            "id": workspace.id,
            "business_id": workspace.business_id,
            "name": workspace.name,
            "status": workspace.status,
        }

    except Exception as e:
        logger.exception(f"Error creating workspace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workspace: {str(e)}"
        )
