"""Indicator endpoints for IOCs (Indicators of Compromise)."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_with_org, require_role
from app.crud.indicator import (
    bulk_create_indicators,
    create_indicator,
    delete_indicator,
    get_indicator,
    get_indicators_by_org,
    get_indicators_by_type,
    get_recent_indicators,
    mark_as_false_positive,
    mark_as_active,
    search_indicators,
    update_indicator,
)
from app.db.session import get_db
from app.schemas.auth import Principal

router = APIRouter(prefix="/indicators", tags=["indicators"])


# ==========================================
# Request/Response Schemas
# ==========================================


class CreateIndicatorRequest(BaseModel):
    """Request to create indicator."""

    type: str = Field(..., min_length=1, max_length=50)
    value: str = Field(..., min_length=1)
    project_id: Optional[UUID] = None
    description: Optional[str] = None
    classification: Optional[str] = Field(None, pattern="^(malicious|suspicious|benign|unknown)$")
    confidence: Optional[int] = Field(None, ge=0, le=100)
    severity: Optional[str] = Field(None, pattern="^(critical|high|medium|low|info)$")
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    source: Optional[str] = Field(None, max_length=200)
    tags: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    mitre_techniques: List[str] = Field(default_factory=list)


class UpdateIndicatorRequest(BaseModel):
    """Request to update indicator."""

    description: Optional[str] = None
    classification: Optional[str] = Field(None, pattern="^(malicious|suspicious|benign|unknown)$")
    confidence: Optional[int] = Field(None, ge=0, le=100)
    severity: Optional[str] = Field(None, pattern="^(critical|high|medium|low|info)$")
    last_seen: Optional[datetime] = None
    tags: Optional[List[str]] = None
    mitre_tactics: Optional[List[str]] = None
    mitre_techniques: Optional[List[str]] = None
    active: Optional[bool] = None
    false_positive: Optional[bool] = None


class IndicatorResponse(BaseModel):
    """Indicator response."""

    id: UUID
    org_id: UUID
    project_id: Optional[UUID]
    type: str
    value: str
    description: Optional[str]
    classification: Optional[str]
    confidence: Optional[int]
    severity: Optional[str]
    first_seen: Optional[str]
    last_seen: Optional[str]
    source: Optional[str]
    tags: List[str]
    mitre_tactics: List[str]
    mitre_techniques: List[str]
    enrichment: dict
    active: bool
    false_positive: bool
    created_at: str
    updated_at: str
    created_by: UUID

    class Config:
        from_attributes = True


class BulkCreateIndicatorsRequest(BaseModel):
    """Request to bulk create indicators."""

    project_id: Optional[UUID] = None
    indicators: List[dict] = Field(..., min_items=1, max_items=1000)


class BulkCreateIndicatorsResponse(BaseModel):
    """Response from bulk create."""

    created_count: int
    indicators: List[IndicatorResponse]


# ==========================================
# Indicator Endpoints
# ==========================================


@router.get("", response_model=List[IndicatorResponse])
async def list_indicators(
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
    project_id: Optional[UUID] = Query(None),
    type_filter: Optional[str] = Query(None),
    active_only: bool = Query(True),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    List indicators for organization.

    Filter by project, type, and active status.
    """
    indicators = await get_indicators_by_org(
        db,
        org_id=principal.org_id,
        project_id=project_id,
        type_filter=type_filter,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )

    return [
        IndicatorResponse(
            id=i.id,
            org_id=i.org_id,
            project_id=i.project_id,
            type=i.type,
            value=i.value,
            description=i.description,
            classification=i.classification,
            confidence=i.confidence,
            severity=i.severity,
            first_seen=i.first_seen.isoformat() if i.first_seen else None,
            last_seen=i.last_seen.isoformat() if i.last_seen else None,
            source=i.source,
            tags=i.tags or [],
            mitre_tactics=i.mitre_tactics or [],
            mitre_techniques=i.mitre_techniques or [],
            enrichment=i.enrichment or {},
            active=i.active,
            false_positive=i.false_positive,
            created_at=i.created_at.isoformat(),
            updated_at=i.updated_at.isoformat(),
            created_by=i.created_by,
        )
        for i in indicators
    ]


@router.get("/search", response_model=List[IndicatorResponse])
async def search_indicators_endpoint(
    q: str = Query(..., min_length=1),
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, le=500),
):
    """
    Search indicators by value or description.

    Use query parameter `q` for search string.
    """
    indicators = await search_indicators(
        db,
        org_id=principal.org_id,
        query_string=q,
        limit=limit,
    )

    return [
        IndicatorResponse(
            id=i.id,
            org_id=i.org_id,
            project_id=i.project_id,
            type=i.type,
            value=i.value,
            description=i.description,
            classification=i.classification,
            confidence=i.confidence,
            severity=i.severity,
            first_seen=i.first_seen.isoformat() if i.first_seen else None,
            last_seen=i.last_seen.isoformat() if i.last_seen else None,
            source=i.source,
            tags=i.tags or [],
            mitre_tactics=i.mitre_tactics or [],
            mitre_techniques=i.mitre_techniques or [],
            enrichment=i.enrichment or {},
            active=i.active,
            false_positive=i.false_positive,
            created_at=i.created_at.isoformat(),
            updated_at=i.updated_at.isoformat(),
            created_by=i.created_by,
        )
        for i in indicators
    ]


@router.get("/recent", response_model=List[IndicatorResponse])
async def get_recent_indicators_endpoint(
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(50, le=500),
):
    """
    Get recently created indicators.

    Returns indicators created within the last N days.
    """
    indicators = await get_recent_indicators(
        db,
        org_id=principal.org_id,
        days=days,
        limit=limit,
    )

    return [
        IndicatorResponse(
            id=i.id,
            org_id=i.org_id,
            project_id=i.project_id,
            type=i.type,
            value=i.value,
            description=i.description,
            classification=i.classification,
            confidence=i.confidence,
            severity=i.severity,
            first_seen=i.first_seen.isoformat() if i.first_seen else None,
            last_seen=i.last_seen.isoformat() if i.last_seen else None,
            source=i.source,
            tags=i.tags or [],
            mitre_tactics=i.mitre_tactics or [],
            mitre_techniques=i.mitre_techniques or [],
            enrichment=i.enrichment or {},
            active=i.active,
            false_positive=i.false_positive,
            created_at=i.created_at.isoformat(),
            updated_at=i.updated_at.isoformat(),
            created_by=i.created_by,
        )
        for i in indicators
    ]


@router.post("", response_model=IndicatorResponse, status_code=status.HTTP_201_CREATED)
async def create_indicator_endpoint(
    request: CreateIndicatorRequest,
    principal: Principal = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new indicator.

    Requires editor role or higher.
    """
    indicator = await create_indicator(
        db,
        org_id=principal.org_id,
        type=request.type,
        value=request.value,
        created_by=principal.user_id,
        project_id=request.project_id,
        description=request.description,
        classification=request.classification,
        confidence=request.confidence,
        severity=request.severity,
        first_seen=request.first_seen,
        last_seen=request.last_seen,
        source=request.source,
        tags=request.tags,
        mitre_tactics=request.mitre_tactics,
        mitre_techniques=request.mitre_techniques,
    )

    return IndicatorResponse(
        id=indicator.id,
        org_id=indicator.org_id,
        project_id=indicator.project_id,
        type=indicator.type,
        value=indicator.value,
        description=indicator.description,
        classification=indicator.classification,
        confidence=indicator.confidence,
        severity=indicator.severity,
        first_seen=indicator.first_seen.isoformat() if indicator.first_seen else None,
        last_seen=indicator.last_seen.isoformat() if indicator.last_seen else None,
        source=indicator.source,
        tags=indicator.tags or [],
        mitre_tactics=indicator.mitre_tactics or [],
        mitre_techniques=indicator.mitre_techniques or [],
        enrichment=indicator.enrichment or {},
        active=indicator.active,
        false_positive=indicator.false_positive,
        created_at=indicator.created_at.isoformat(),
        updated_at=indicator.updated_at.isoformat(),
        created_by=indicator.created_by,
    )


@router.post("/bulk", response_model=BulkCreateIndicatorsResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_indicators_endpoint(
    request: BulkCreateIndicatorsRequest,
    principal: Principal = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk create indicators (up to 1000 at a time).

    Requires editor role or higher.
    """
    indicators = await bulk_create_indicators(
        db,
        org_id=principal.org_id,
        created_by=principal.user_id,
        indicators=request.indicators,
        project_id=request.project_id,
    )

    return BulkCreateIndicatorsResponse(
        created_count=len(indicators),
        indicators=[
            IndicatorResponse(
                id=i.id,
                org_id=i.org_id,
                project_id=i.project_id,
                type=i.type,
                value=i.value,
                description=i.description,
                classification=i.classification,
                confidence=i.confidence,
                severity=i.severity,
                first_seen=i.first_seen.isoformat() if i.first_seen else None,
                last_seen=i.last_seen.isoformat() if i.last_seen else None,
                source=i.source,
                tags=i.tags or [],
                mitre_tactics=i.mitre_tactics or [],
                mitre_techniques=i.mitre_techniques or [],
                enrichment=i.enrichment or {},
                active=i.active,
                false_positive=i.false_positive,
                created_at=i.created_at.isoformat(),
                updated_at=i.updated_at.isoformat(),
                created_by=i.created_by,
            )
            for i in indicators
        ],
    )


@router.get("/{indicator_id}", response_model=IndicatorResponse)
async def get_indicator_endpoint(
    indicator_id: UUID,
    principal: Principal = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Get indicator details.

    Indicator must belong to user's organization.
    """
    indicator = await get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    # Verify org ownership
    if indicator.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return IndicatorResponse(
        id=indicator.id,
        org_id=indicator.org_id,
        project_id=indicator.project_id,
        type=indicator.type,
        value=indicator.value,
        description=indicator.description,
        classification=indicator.classification,
        confidence=indicator.confidence,
        severity=indicator.severity,
        first_seen=indicator.first_seen.isoformat() if indicator.first_seen else None,
        last_seen=indicator.last_seen.isoformat() if indicator.last_seen else None,
        source=indicator.source,
        tags=indicator.tags or [],
        mitre_tactics=indicator.mitre_tactics or [],
        mitre_techniques=indicator.mitre_techniques or [],
        enrichment=indicator.enrichment or {},
        active=indicator.active,
        false_positive=indicator.false_positive,
        created_at=indicator.created_at.isoformat(),
        updated_at=indicator.updated_at.isoformat(),
        created_by=indicator.created_by,
    )


@router.patch("/{indicator_id}", response_model=IndicatorResponse)
async def update_indicator_endpoint(
    indicator_id: UUID,
    request: UpdateIndicatorRequest,
    principal: Principal = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update indicator.

    Requires editor role or higher.
    """
    # Verify indicator exists and belongs to org
    indicator = await get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    if indicator.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update indicator
    updated_indicator = await update_indicator(
        db,
        indicator_id=indicator_id,
        description=request.description,
        classification=request.classification,
        confidence=request.confidence,
        severity=request.severity,
        last_seen=request.last_seen,
        tags=request.tags,
        mitre_tactics=request.mitre_tactics,
        mitre_techniques=request.mitre_techniques,
        active=request.active,
        false_positive=request.false_positive,
    )

    if not updated_indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    return IndicatorResponse(
        id=updated_indicator.id,
        org_id=updated_indicator.org_id,
        project_id=updated_indicator.project_id,
        type=updated_indicator.type,
        value=updated_indicator.value,
        description=updated_indicator.description,
        classification=updated_indicator.classification,
        confidence=updated_indicator.confidence,
        severity=updated_indicator.severity,
        first_seen=updated_indicator.first_seen.isoformat() if updated_indicator.first_seen else None,
        last_seen=updated_indicator.last_seen.isoformat() if updated_indicator.last_seen else None,
        source=updated_indicator.source,
        tags=updated_indicator.tags or [],
        mitre_tactics=updated_indicator.mitre_tactics or [],
        mitre_techniques=updated_indicator.mitre_techniques or [],
        enrichment=updated_indicator.enrichment or {},
        active=updated_indicator.active,
        false_positive=updated_indicator.false_positive,
        created_at=updated_indicator.created_at.isoformat(),
        updated_at=updated_indicator.updated_at.isoformat(),
        created_by=updated_indicator.created_by,
    )


@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_indicator_endpoint(
    indicator_id: UUID,
    principal: Principal = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete indicator.

    Requires admin role or higher.
    """
    # Verify indicator exists and belongs to org
    indicator = await get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    if indicator.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete indicator
    success = await delete_indicator(db, indicator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Indicator not found")

    return None


@router.post("/{indicator_id}/mark-false-positive", response_model=IndicatorResponse)
async def mark_false_positive_endpoint(
    indicator_id: UUID,
    principal: Principal = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark indicator as false positive.

    This will deactivate the indicator.
    Requires editor role or higher.
    """
    # Verify indicator exists and belongs to org
    indicator = await get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    if indicator.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Mark as false positive
    updated_indicator = await mark_as_false_positive(db, indicator_id)
    if not updated_indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    return IndicatorResponse(
        id=updated_indicator.id,
        org_id=updated_indicator.org_id,
        project_id=updated_indicator.project_id,
        type=updated_indicator.type,
        value=updated_indicator.value,
        description=updated_indicator.description,
        classification=updated_indicator.classification,
        confidence=updated_indicator.confidence,
        severity=updated_indicator.severity,
        first_seen=updated_indicator.first_seen.isoformat() if updated_indicator.first_seen else None,
        last_seen=updated_indicator.last_seen.isoformat() if updated_indicator.last_seen else None,
        source=updated_indicator.source,
        tags=updated_indicator.tags or [],
        mitre_tactics=updated_indicator.mitre_tactics or [],
        mitre_techniques=updated_indicator.mitre_techniques or [],
        enrichment=updated_indicator.enrichment or {},
        active=updated_indicator.active,
        false_positive=updated_indicator.false_positive,
        created_at=updated_indicator.created_at.isoformat(),
        updated_at=updated_indicator.updated_at.isoformat(),
        created_by=updated_indicator.created_by,
    )


@router.post("/{indicator_id}/activate", response_model=IndicatorResponse)
async def activate_indicator_endpoint(
    indicator_id: UUID,
    principal: Principal = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate indicator (unmark as false positive).

    Requires editor role or higher.
    """
    # Verify indicator exists and belongs to org
    indicator = await get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    if indicator.org_id != principal.org_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Mark as active
    updated_indicator = await mark_as_active(db, indicator_id)
    if not updated_indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")

    return IndicatorResponse(
        id=updated_indicator.id,
        org_id=updated_indicator.org_id,
        project_id=updated_indicator.project_id,
        type=updated_indicator.type,
        value=updated_indicator.value,
        description=updated_indicator.description,
        classification=updated_indicator.classification,
        confidence=updated_indicator.confidence,
        severity=updated_indicator.severity,
        first_seen=updated_indicator.first_seen.isoformat() if updated_indicator.first_seen else None,
        last_seen=updated_indicator.last_seen.isoformat() if updated_indicator.last_seen else None,
        source=updated_indicator.source,
        tags=updated_indicator.tags or [],
        mitre_tactics=updated_indicator.mitre_tactics or [],
        mitre_techniques=updated_indicator.mitre_techniques or [],
        enrichment=updated_indicator.enrichment or {},
        active=updated_indicator.active,
        false_positive=updated_indicator.false_positive,
        created_at=updated_indicator.created_at.isoformat(),
        updated_at=updated_indicator.updated_at.isoformat(),
        created_by=updated_indicator.created_by,
    )
