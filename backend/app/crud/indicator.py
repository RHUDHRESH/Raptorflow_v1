"""CRUD operations for indicators."""

from uuid import UUID
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threat_intel import Indicator


async def get_indicator(db: AsyncSession, indicator_id: UUID) -> Optional[Indicator]:
    """Get indicator by ID."""
    return await db.get(Indicator, indicator_id)


async def get_indicators_by_org(
    db: AsyncSession,
    org_id: UUID,
    project_id: Optional[UUID] = None,
    type_filter: Optional[str] = None,
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> List[Indicator]:
    """
    Get indicators for an organization.

    Args:
        db: Database session
        org_id: Organization ID
        project_id: Optional project filter
        type_filter: Optional indicator type filter
        active_only: Only return active indicators
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of indicators
    """
    query = select(Indicator).filter(Indicator.org_id == org_id)

    if project_id:
        query = query.filter(Indicator.project_id == project_id)

    if type_filter:
        query = query.filter(Indicator.type == type_filter)

    if active_only:
        query = query.filter(
            Indicator.active == True,
            Indicator.false_positive == False,
        )

    query = query.order_by(Indicator.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


async def search_indicators(
    db: AsyncSession,
    org_id: UUID,
    query_string: str,
    limit: int = 50,
) -> List[Indicator]:
    """
    Search indicators by value.

    Args:
        db: Database session
        org_id: Organization ID
        query_string: Search query
        limit: Maximum number of results

    Returns:
        List of matching indicators
    """
    search_query = select(Indicator).filter(
        Indicator.org_id == org_id,
        or_(
            Indicator.value.ilike(f"%{query_string}%"),
            Indicator.description.ilike(f"%{query_string}%"),
        ),
    )

    search_query = search_query.order_by(Indicator.created_at.desc()).limit(limit)

    result = await db.execute(search_query)
    return list(result.scalars().all())


async def create_indicator(
    db: AsyncSession,
    org_id: UUID,
    type: str,
    value: str,
    created_by: UUID,
    project_id: Optional[UUID] = None,
    description: Optional[str] = None,
    classification: Optional[str] = None,
    confidence: Optional[int] = None,
    severity: Optional[str] = None,
    first_seen: Optional[datetime] = None,
    last_seen: Optional[datetime] = None,
    source: Optional[str] = None,
    tags: Optional[List[str]] = None,
    mitre_tactics: Optional[List[str]] = None,
    mitre_techniques: Optional[List[str]] = None,
) -> Indicator:
    """
    Create new indicator.

    Args:
        db: Database session
        org_id: Organization ID
        type: Indicator type (ip, domain, url, hash, email, etc.)
        value: Indicator value
        created_by: User ID who created the indicator
        project_id: Optional project association
        description: Optional description
        classification: malicious, suspicious, benign, unknown
        confidence: 0-100
        severity: critical, high, medium, low, info
        first_seen: First seen timestamp
        last_seen: Last seen timestamp
        source: Source of the indicator
        tags: Optional tags
        mitre_tactics: MITRE ATT&CK tactics
        mitre_techniques: MITRE ATT&CK techniques

    Returns:
        Created indicator
    """
    indicator = Indicator(
        org_id=org_id,
        project_id=project_id,
        type=type,
        value=value,
        description=description,
        classification=classification,
        confidence=confidence,
        severity=severity,
        first_seen=first_seen,
        last_seen=last_seen,
        source=source,
        tags=tags or [],
        mitre_tactics=mitre_tactics or [],
        mitre_techniques=mitre_techniques or [],
        created_by=created_by,
    )

    db.add(indicator)
    await db.commit()
    await db.refresh(indicator)
    return indicator


async def update_indicator(
    db: AsyncSession,
    indicator_id: UUID,
    description: Optional[str] = None,
    classification: Optional[str] = None,
    confidence: Optional[int] = None,
    severity: Optional[str] = None,
    last_seen: Optional[datetime] = None,
    tags: Optional[List[str]] = None,
    mitre_tactics: Optional[List[str]] = None,
    mitre_techniques: Optional[List[str]] = None,
    enrichment: Optional[dict] = None,
    active: Optional[bool] = None,
    false_positive: Optional[bool] = None,
) -> Optional[Indicator]:
    """
    Update indicator.

    Args:
        db: Database session
        indicator_id: Indicator ID
        description: Updated description
        classification: Updated classification
        confidence: Updated confidence score
        severity: Updated severity
        last_seen: Updated last seen timestamp
        tags: Updated tags
        mitre_tactics: Updated MITRE tactics
        mitre_techniques: Updated MITRE techniques
        enrichment: Additional enrichment data (merged)
        active: Active status
        false_positive: False positive flag

    Returns:
        Updated indicator or None if not found
    """
    indicator = await db.get(Indicator, indicator_id)
    if not indicator:
        return None

    if description is not None:
        indicator.description = description
    if classification is not None:
        indicator.classification = classification
    if confidence is not None:
        indicator.confidence = confidence
    if severity is not None:
        indicator.severity = severity
    if last_seen is not None:
        indicator.last_seen = last_seen
    if tags is not None:
        indicator.tags = tags
    if mitre_tactics is not None:
        indicator.mitre_tactics = mitre_tactics
    if mitre_techniques is not None:
        indicator.mitre_techniques = mitre_techniques
    if enrichment is not None:
        # Merge enrichment data
        indicator.enrichment = {**(indicator.enrichment or {}), **enrichment}
    if active is not None:
        indicator.active = active
    if false_positive is not None:
        indicator.false_positive = false_positive

    await db.commit()
    await db.refresh(indicator)
    return indicator


async def delete_indicator(db: AsyncSession, indicator_id: UUID) -> bool:
    """
    Delete indicator.

    Args:
        db: Database session
        indicator_id: Indicator ID

    Returns:
        True if deleted, False if not found
    """
    indicator = await db.get(Indicator, indicator_id)
    if not indicator:
        return False

    await db.delete(indicator)
    await db.commit()
    return True


async def mark_as_false_positive(
    db: AsyncSession,
    indicator_id: UUID,
) -> Optional[Indicator]:
    """Mark indicator as false positive."""
    return await update_indicator(db, indicator_id, false_positive=True, active=False)


async def mark_as_active(
    db: AsyncSession,
    indicator_id: UUID,
) -> Optional[Indicator]:
    """Mark indicator as active."""
    return await update_indicator(db, indicator_id, false_positive=False, active=True)


async def bulk_create_indicators(
    db: AsyncSession,
    org_id: UUID,
    created_by: UUID,
    indicators: List[dict],
    project_id: Optional[UUID] = None,
) -> List[Indicator]:
    """
    Bulk create indicators.

    Args:
        db: Database session
        org_id: Organization ID
        created_by: User ID who created the indicators
        indicators: List of indicator dictionaries with 'type' and 'value' required
        project_id: Optional project association

    Returns:
        List of created indicators
    """
    created_indicators = []

    for ind_data in indicators:
        indicator = Indicator(
            org_id=org_id,
            project_id=project_id,
            type=ind_data["type"],
            value=ind_data["value"],
            description=ind_data.get("description"),
            classification=ind_data.get("classification"),
            confidence=ind_data.get("confidence"),
            severity=ind_data.get("severity"),
            tags=ind_data.get("tags", []),
            created_by=created_by,
        )
        db.add(indicator)
        created_indicators.append(indicator)

    await db.commit()

    # Refresh all created indicators
    for indicator in created_indicators:
        await db.refresh(indicator)

    return created_indicators


async def get_indicators_by_type(
    db: AsyncSession,
    org_id: UUID,
    indicator_type: str,
    limit: int = 100,
) -> List[Indicator]:
    """Get all indicators of a specific type."""
    return await get_indicators_by_org(
        db,
        org_id=org_id,
        type_filter=indicator_type,
        limit=limit,
    )


async def get_recent_indicators(
    db: AsyncSession,
    org_id: UUID,
    days: int = 7,
    limit: int = 50,
) -> List[Indicator]:
    """
    Get recently created indicators.

    Args:
        db: Database session
        org_id: Organization ID
        days: Number of days to look back
        limit: Maximum number of results

    Returns:
        List of recent indicators
    """
    from datetime import timedelta

    recent_date = datetime.utcnow() - timedelta(days=days)

    query = select(Indicator).filter(
        Indicator.org_id == org_id,
        Indicator.created_at >= recent_date,
    )

    query = query.order_by(Indicator.created_at.desc()).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())
